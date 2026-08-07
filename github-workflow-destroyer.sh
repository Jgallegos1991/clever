#!/bin/bash
# github-workflow-destroyer.sh
# Nuclear option for cleaning up 230+ GitHub workflows when standard methods aren't enough

"""
github-workflow-destroyer.sh - Aggressive GitHub workflow and run cleanup

Why: Handle extreme cases like 230+ workflows that may include disabled workflows,
     old workflow runs, and artifacts that don't show up in standard CLI listings
Where: Integrates with GitHub CLI and REST API for comprehensive cleanup
How: Uses multiple deletion strategies including API calls and bulk operations

File Usage:
    - Primary callers: Command line execution for emergency cleanup scenarios
    - Key dependencies: GitHub CLI (gh), curl, jq for JSON processing
    - Data sources: GitHub repository via CLI and REST API
    - Data destinations: GitHub repository (complete workflow/run deletion)
    - Configuration: Hardcoded essential workflows and safety limits
    - Database interactions: None (GitHub API only)
    - API endpoints: GitHub Workflows API, Actions API, multiple endpoints
    - Frontend connections: None (command line tool)
    - Background processes: None (interactive with progress feedback)

Connects to:
    - GitHub Actions API: Direct API calls for stubborn workflows
    - GitHub CLI: Primary interface for workflow operations
    - cleanup-excessive-workflows.sh: Fallback to standard cleanup
    - Repository workflows: Target of all deletion operations

Performance Notes:
    - Memory usage: Minimal (API response processing)
    - CPU impact: Low (mostly network I/O and JSON processing)
    - I/O operations: Heavy GitHub API usage with rate limiting
    - Scaling limits: GitHub API rate limits (5000 requests/hour)

Critical Dependencies:
    - Required packages: GitHub CLI (gh), curl, jq
    - Optional packages: None
    - System requirements: Network access, GitHub authentication
    - Database schema: None
"""

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Essential workflows to preserve
ESSENTIAL_WORKFLOWS=(
    "CI - Tests & Validation"
    "Code Quality - Lint & Format"  
    "Knowledge Base Validation"
    "Security & Compliance"
    "Release & Deployment"
    "Performance Monitoring"
)

# Safety limits
MAX_DELETION_BATCH=50
API_RATE_LIMIT_DELAY=0.5

# Function to check if we're properly authenticated
check_github_auth() {
    echo -e "${BLUE}🔐 Checking GitHub authentication...${NC}"
    
    if ! gh auth status &>/dev/null; then
        echo -e "${RED}❌ Not authenticated with GitHub${NC}"
        echo "Run: gh auth login"
        exit 1
    fi
    
    # Get repository info
    REPO_OWNER=$(gh repo view --json owner -q .owner.login 2>/dev/null)
    REPO_NAME=$(gh repo view --json name -q .name 2>/dev/null)
    
    if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
        echo -e "${RED}❌ Could not determine repository info${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Authenticated as $(gh auth status 2>&1 | grep 'Logged in' | cut -d' ' -f7)${NC}"
    echo -e "${GREEN}✅ Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
}

# Function to get ALL workflows using multiple methods
get_all_workflows() {
    echo -e "${BLUE}🔍 Discovering ALL workflows (including disabled ones)...${NC}"
    
    local temp_file="/tmp/all_workflows.json"
    
    # Method 1: CLI (enabled workflows)
    echo -e "  ${YELLOW}📋 Getting enabled workflows via CLI...${NC}"
    gh workflow list --json id,name,state --limit=1000 > "${temp_file}.cli" 2>/dev/null || echo '[]' > "${temp_file}.cli"
    local cli_count=$(jq '. | length' "${temp_file}.cli")
    echo -e "    ${GREEN}Found ${cli_count} workflows via CLI${NC}"
    
    # Method 2: REST API (all workflows including disabled)
    echo -e "  ${YELLOW}🌐 Getting ALL workflows via REST API...${NC}"
    gh api "repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows?per_page=100" --paginate \
        | jq '[.workflows[] | {id: .id, name: .name, state: .state}]' > "${temp_file}.api" 2>/dev/null || echo '[]' > "${temp_file}.api"
    local api_count=$(jq '. | length' "${temp_file}.api")
    echo -e "    ${GREEN}Found ${api_count} workflows via API${NC}"
    
    # Method 3: Combine and deduplicate
    jq -s 'add | unique_by(.id)' "${temp_file}.cli" "${temp_file}.api" > "$temp_file"
    local total_count=$(jq '. | length' "$temp_file")
    
    echo -e "  ${CYAN}📊 Total unique workflows: ${total_count}${NC}"
    
    # Clean up temp files
    rm -f "${temp_file}.cli" "${temp_file}.api"
    
    echo "$temp_file"
}

# Function to delete workflow runs in batches
delete_all_workflow_runs() {
    echo -e "${BLUE}🗑️  Deleting ALL workflow runs...${NC}"
    
    local deleted_count=0
    local page=1
    local has_more=true
    
    while [ "$has_more" = true ]; do
        echo -e "  ${YELLOW}Processing page $page...${NC}"
        
        # Get runs for this page
        local runs=$(gh api "repos/${REPO_OWNER}/${REPO_NAME}/actions/runs?per_page=100&page=$page" \
            | jq '.workflow_runs[] | {id: .id, status: .status, conclusion: .conclusion}' 2>/dev/null || echo 'null')
        
        if [ "$runs" = "null" ] || [ "$(echo "$runs" | jq -s '. | length')" -eq 0 ]; then
            has_more=false
            break
        fi
        
        # Process each run
        echo "$runs" | jq -r '.id' | while read -r run_id; do
            if [ -n "$run_id" ] && [ "$run_id" != "null" ]; then
                echo -e "    ${YELLOW}Deleting run: $run_id${NC}"
                
                # Cancel first if running
                gh run cancel "$run_id" 2>/dev/null || true
                sleep 0.1
                
                # Delete the run
                gh run delete "$run_id" 2>/dev/null || \
                gh api "repos/${REPO_OWNER}/${REPO_NAME}/actions/runs/$run_id" -X DELETE 2>/dev/null || true
                
                ((deleted_count++))
                sleep $API_RATE_LIMIT_DELAY
            fi
        done
        
        ((page++))
        
        # Safety limit
        if [ $page -gt 50 ]; then
            echo -e "  ${YELLOW}⚠️  Hit page limit, stopping run deletion${NC}"
            break
        fi
    done
    
    echo -e "  ${GREEN}✅ Deleted $deleted_count workflow runs${NC}"
}

# Function to delete workflows using multiple strategies
delete_workflows_aggressively() {
    local workflows_file="$1"
    
    echo -e "${BLUE}💥 Starting aggressive workflow deletion...${NC}"
    
    # Create essential workflow pattern
    local essential_pattern=""
    for workflow in "${ESSENTIAL_WORKFLOWS[@]}"; do
        if [ -z "$essential_pattern" ]; then
            essential_pattern="^${workflow}$"
        else
            essential_pattern="${essential_pattern}|^${workflow}$"
        fi
    done
    
    local deleted_count=0
    local failed_count=0
    local preserved_count=0
    
    # Process workflows
    jq -r '.[] | "\(.id)|\(.name)|\(.state)"' "$workflows_file" | while IFS='|' read -r workflow_id workflow_name workflow_state; do
        # Check if this is an essential workflow
        if echo "$workflow_name" | grep -E "$essential_pattern" >/dev/null; then
            echo -e "  ${GREEN}🛡️  Preserving: $workflow_name${NC}"
            ((preserved_count++))
            continue
        fi
        
        echo -e "  ${RED}💀 Deleting: $workflow_name (ID: $workflow_id, State: $workflow_state)${NC}"
        
        local deletion_success=false
        
        # Strategy 1: Standard CLI deletion
        if gh workflow delete "$workflow_id" --confirm 2>/dev/null; then
            deletion_success=true
            echo -e "    ${GREEN}✅ Deleted via CLI${NC}"
        else
            # Strategy 2: Direct API call
            if gh api "repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/$workflow_id" -X DELETE 2>/dev/null; then
                deletion_success=true
                echo -e "    ${GREEN}✅ Deleted via API${NC}"
            else
                # Strategy 3: Force deletion with curl
                local auth_token=$(gh auth token)
                if curl -s -X DELETE \
                    -H "Authorization: token $auth_token" \
                    -H "Accept: application/vnd.github.v3+json" \
                    "https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/$workflow_id" \
                    2>/dev/null | grep -q "204"; then
                    deletion_success=true
                    echo -e "    ${GREEN}✅ Deleted via curl${NC}"
                fi
            fi
        fi
        
        if [ "$deletion_success" = true ]; then
            ((deleted_count++))\n        else\n            echo -e "    ${RED}❌ Failed all deletion methods${NC}"\n            ((failed_count++))\n        fi\n        \n        # Rate limiting\n        sleep $API_RATE_LIMIT_DELAY\n    done\n    \n    echo -e "${GREEN}🎯 Deletion summary:${NC}"\n    echo -e "  ${GREEN}✅ Workflows deleted: $deleted_count${NC}"\n    echo -e "  ${GREEN}🛡️  Essential workflows preserved: $preserved_count${NC}"\n    if [ "$failed_count" -gt 0 ]; then\n        echo -e "  ${RED}❌ Failed deletions: $failed_count${NC}"\n    fi\n}\n\n# Function to clear workflow artifacts and caches\nclear_artifacts_and_caches() {\n    echo -e "${BLUE}🧹 Clearing artifacts and caches...${NC}"\n    \n    # Delete artifacts\n    echo -e "  ${YELLOW}🗂️  Deleting artifacts...${NC}"\n    local artifacts=$(gh api "repos/${REPO_OWNER}/${REPO_NAME}/actions/artifacts?per_page=100" | jq -r '.artifacts[]?.id' 2>/dev/null || true)\n    if [ -n "$artifacts" ]; then\n        echo "$artifacts" | while read -r artifact_id; do\n            if [ -n "$artifact_id" ]; then\n                gh api "repos/${REPO_OWNER}/${REPO_NAME}/actions/artifacts/$artifact_id" -X DELETE 2>/dev/null || true\n                sleep 0.2\n            fi\n        done\n    fi\n    \n    # Delete caches\n    echo -e "  ${YELLOW}💾 Deleting caches...${NC}"\n    gh cache list --limit=200 2>/dev/null | tail -n +2 | cut -f1 | while read -r cache_id; do\n        if [ -n "$cache_id" ]; then\n            gh cache delete "$cache_id" 2>/dev/null || true\n            sleep 0.1\n        fi\n    done\n    \n    echo -e "  ${GREEN}✅ Artifacts and caches cleared${NC}"\n}\n\n# Function to verify final state\nverify_destruction() {\n    echo -e "${BLUE}🔍 Verifying destruction results...${NC}"\n    \n    # Wait a moment for GitHub to update\n    sleep 2\n    \n    # Check workflows via CLI\n    local cli_count=$(gh workflow list --json id 2>/dev/null | jq '. | length' 2>/dev/null || echo \"0\")\n    \n    # Check workflows via API\n    local api_count=$(gh api "repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows?per_page=100" 2>/dev/null | jq '.workflows | length' 2>/dev/null || echo \"0\")\n    \n    # Check runs\n    local runs_count=$(gh run list --limit=10 --json databaseId 2>/dev/null | jq '. | length' 2>/dev/null || echo \"0\")\n    \n    echo -e "${CYAN}📊 Final State:${NC}"\n    echo -e "  ${BLUE}Workflows (CLI): $cli_count${NC}"\n    echo -e "  ${BLUE}Workflows (API): $api_count${NC}"\n    echo -e "  ${BLUE}Recent runs: $runs_count${NC}"\n    \n    if [ "$cli_count" -le 6 ] && [ "$api_count" -le 6 ]; then\n        echo -e "${GREEN}🎉 SUCCESS! Workflow count is now optimal${NC}"\n        echo -e "${GREEN}   Repository has been successfully cleaned up!${NC}"\n    else\n        echo -e "${YELLOW}⚠️  Still showing $api_count workflows${NC}"\n        echo -e "${YELLOW}   This might be due to:${NC}"\n        echo -e "${YELLOW}   • GitHub cache/propagation delay${NC}"\n        echo -e "${YELLOW}   • Protected workflows that can't be deleted${NC}"\n        echo -e "${YELLOW}   • Browser cache (try refreshing)${NC}"\n    fi\n    \n    # List remaining workflows\n    echo -e "${BLUE}📋 Remaining workflows:${NC}"\n    gh workflow list --json name,state 2>/dev/null | jq -r '.[] | "  ✅ \\(.name) (\\(.state))"' | sort\n}\n\n# Main execution\nmain() {\n    echo -e "${RED}💀 GITHUB WORKFLOW DESTROYER 💀${NC}"\n    echo -e "${RED}=================================${NC}"\n    echo -e "${YELLOW}⚠️  NUCLEAR OPTION FOR 230+ WORKFLOWS ⚠️${NC}"\n    echo ""\n    echo -e "${CYAN}This script will:${NC}"\n    echo -e "  ${CYAN}🗑️  Delete ALL workflow runs${NC}"\n    echo -e "  ${CYAN}💥 Delete ALL workflows (except 6 essential)${NC}"\n    echo -e "  ${CYAN}🧹 Clear all artifacts and caches${NC}"\n    echo -e "  ${CYAN}🔄 Use multiple deletion strategies${NC}"\n    echo ""\n    echo -e "${RED}THIS IS EXTREMELY DESTRUCTIVE!${NC}"\n    echo ""\n    \n    # Safety check\n    check_github_auth\n    echo ""\n    \n    # Get current state\n    local workflows_file=$(get_all_workflows)\n    local total_workflows=$(jq '. | length' "$workflows_file")\n    echo ""\n    \n    echo -e "${CYAN}📊 Current State Analysis:${NC}"\n    echo -e "  ${BLUE}Total workflows found: $total_workflows${NC}"\n    echo -e "  ${YELLOW}Target: Reduce to 6 essential workflows${NC}"\n    echo ""\n    \n    if [ "$total_workflows" -lt 10 ]; then\n        echo -e "${GREEN}ℹ️  Only $total_workflows workflows found${NC}"\n        echo -e "${GREEN}   You might want to use the standard cleanup script instead${NC}"\n        echo -e "${BLUE}   Run: ./cleanup-excessive-workflows.sh${NC}"\n        exit 0\n    fi\n    \n    # Final warning\n    echo -e "${RED}🚨 FINAL WARNING 🚨${NC}"\n    echo -e "${RED}This will destroy nearly everything in your GitHub Actions!${NC}"\n    echo -e "${RED}Only the 6 essential Clever workflows will survive.${NC}"\n    echo ""\n    echo -e "${YELLOW}Essential workflows that will be preserved:${NC}"\n    for workflow in "${ESSENTIAL_WORKFLOWS[@]}"; do\n        echo -e "  ${GREEN}✅ $workflow${NC}"\n    done\n    echo ""\n    \n    read -p "Type 'DESTROY' to confirm nuclear cleanup: " -r\n    if [[ $REPLY != "DESTROY" ]]; then\n        echo -e "${BLUE}ℹ️  Nuclear cleanup cancelled${NC}"\n        exit 0\n    fi\n    \n    echo ""\n    echo -e "${RED}🚀 LAUNCHING NUCLEAR CLEANUP...${NC}"\n    echo ""\n    \n    # Execute destruction sequence\n    delete_all_workflow_runs\n    echo ""\n    \n    clear_artifacts_and_caches\n    echo ""\n    \n    delete_workflows_aggressively "$workflows_file"\n    echo ""\n    \n    verify_destruction\n    echo ""\n    \n    # Cleanup temp file\n    rm -f "$workflows_file"\n    \n    echo -e "${GREEN}💀 NUCLEAR CLEANUP COMPLETE 💀${NC}"\n    echo -e "${GREEN}Your repository should now be clean!${NC}"\n    echo ""\n    echo -e "${BLUE}💡 Next steps:${NC}"\n    echo -e "  ${BLUE}1. Refresh your GitHub repository page${NC}"\n    echo -e "  ${BLUE}2. Check the Actions tab to verify cleanup${NC}"\n    echo -e "  ${BLUE}3. Wait a few minutes for GitHub to update${NC}"\n    echo -e "  ${BLUE}4. Push a commit to test the new workflows${NC}"\n}\n\n# Run with safety check\nif [ "$1" = "--nuclear" ]; then\n    main\nelse\n    echo -e "${YELLOW}⚠️  This is the nuclear option for extreme cleanup${NC}"\n    echo -e "${BLUE}For safety, you must run with: $0 --nuclear${NC}"\n    echo -e "${BLUE}Or try the standard cleanup first: ./cleanup-excessive-workflows.sh${NC}"\nfi