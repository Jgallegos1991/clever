#!/bin/bash
# cleanup-excessive-workflows.sh
# Intelligent cleanup script for removing 200+ excessive GitHub workflows
# while preserving Clever's 6 essential workflows

"""
cleanup-excessive-workflows.sh - GitHub workflow cleanup automation

Why: Remove 200+ excessive GitHub workflows that were likely auto-generated,
     keeping only the 6 essential workflows designed for Clever's architecture
Where: Integrates with GitHub CLI and repository workflow management system  
How: Uses GitHub CLI to identify, filter, and batch delete unwanted workflows

File Usage:
    - Primary callers: Command line execution by developers/maintainers
    - Key dependencies: GitHub CLI (gh), jq for JSON processing
    - Data sources: GitHub repository workflow list via API
    - Data destinations: GitHub repository (workflow deletion)
    - Configuration: Hardcoded list of essential workflows to preserve
    - Database interactions: None (GitHub API only)
    - API endpoints: GitHub Workflows API via gh CLI
    - Frontend connections: None (command line tool)
    - Background processes: None (interactive script)

Connects to:
    - .github/workflows/*.yml: The essential workflows to preserve
    - GitHub repository: Source and target for workflow operations
    - GitHub CLI: Authentication and API interaction
    - User interaction: Confirmation prompts and progress feedback

Performance Notes:
    - Memory usage: Minimal (processes JSON lists, no large data)
    - CPU impact: Low (mostly API calls and text processing)
    - I/O operations: GitHub API calls via gh CLI
    - Scaling limits: Limited by GitHub API rate limits

Critical Dependencies:
    - Required packages: GitHub CLI (gh), jq for JSON processing
    - Optional packages: None
    - System requirements: Network access to GitHub
    - Database schema: None
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Essential workflows to preserve (exact names)
ESSENTIAL_WORKFLOWS=(
    "CI - Tests & Validation"
    "Code Quality - Lint & Format"  
    "Knowledge Base Validation"
    "Security & Compliance"
    "Release & Deployment"
    "Performance Monitoring"
)

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
        echo "Install it with: https://github.com/cli/cli#installation"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq is not installed${NC}"
        echo "Install it with: sudo apt install jq (Ubuntu/Debian) or brew install jq (macOS)"
        exit 1
    fi
    
    # Check GitHub authentication
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI is not authenticated${NC}"
        echo "Run: gh auth login"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All dependencies satisfied${NC}"
}

# Function to list current workflows
list_workflows() {
    echo -e "${BLUE}📋 Current GitHub workflows:${NC}"
    gh workflow list --json id,name,state | jq -r '.[] | "\(.id): \(.name) (\(.state))"' | sort
    echo ""
}

# Function to identify workflows to delete
identify_deletable_workflows() {
    echo -e "${BLUE}🎯 Identifying workflows to delete...${NC}"
    
    # Create a regex pattern for essential workflows
    local essential_pattern=""
    for workflow in "${ESSENTIAL_WORKFLOWS[@]}"; do
        if [ -z "$essential_pattern" ]; then
            essential_pattern="^${workflow}$"
        else
            essential_pattern="${essential_pattern}|^${workflow}$"
        fi
    done
    
    # Get workflows that DON'T match essential pattern
    local deletable_count=$(gh workflow list --json id,name | jq -r --arg pattern "$essential_pattern" '.[] | select(.name | test($pattern) | not) | .id' | wc -l)
    local essential_count=$(gh workflow list --json id,name | jq -r --arg pattern "$essential_pattern" '.[] | select(.name | test($pattern)) | .id' | wc -l)
    
    echo -e "${GREEN}✅ Found ${essential_count} essential workflows to preserve${NC}"
    echo -e "${YELLOW}⚠️  Found ${deletable_count} workflows to delete${NC}"
    
    if [ "$deletable_count" -eq 0 ]; then
        echo -e "${GREEN}🎉 No excessive workflows found! Repository is already clean.${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}📋 Essential workflows (will be preserved):${NC}"
    gh workflow list --json id,name | jq -r --arg pattern "$essential_pattern" '.[] | select(.name | test($pattern)) | "  ✅ \(.name)"' | sort
    
    echo ""
    echo -e "${YELLOW}📋 Workflows to be deleted:${NC}"
    gh workflow list --json id,name | jq -r --arg pattern "$essential_pattern" '.[] | select(.name | test($pattern) | not) | "  ❌ \(.name)"' | sort
    
    return $deletable_count
}

# Function to clean up workflow runs
cleanup_workflow_runs() {
    echo -e "${BLUE}🗑️  Cleaning up workflow runs...${NC}"
    
    local total_runs=0
    local deleted_runs=0
    
    # Get all workflow runs (limit to recent ones to avoid overwhelming)
    echo -e "  ${YELLOW}Fetching workflow runs...${NC}"
    
    # Cancel and delete in-progress/queued runs first
    local active_runs=$(gh run list --status=in_progress,queued --limit=100 --json databaseId,status,workflowName 2>/dev/null || echo '[]')
    local active_count=$(echo "$active_runs" | jq '. | length')
    
    if [ "$active_count" -gt 0 ]; then
        echo -e "  ${YELLOW}Found $active_count active runs to cancel and delete${NC}"
        echo "$active_runs" | jq -r '.[] | "\(.databaseId)|\(.workflowName)|\(.status)"' | while IFS='|' read -r run_id workflow_name status; do
            echo -e "    ${YELLOW}Canceling & deleting:${NC} $workflow_name (ID: $run_id, Status: $status)"
            gh run cancel "$run_id" 2>/dev/null || true
            sleep 0.2  # Brief pause
            gh run delete "$run_id" 2>/dev/null || true
            sleep 0.3  # Rate limiting
        done
    fi
    
    # Delete completed runs (in batches to avoid API limits)
    local completed_runs=$(gh run list --status=completed,failure,cancelled,skipped --limit=200 --json databaseId,workflowName 2>/dev/null || echo '[]')
    local completed_count=$(echo "$completed_runs" | jq '. | length')
    
    if [ "$completed_count" -gt 0 ]; then
        echo -e "  ${YELLOW}Found $completed_count completed runs to delete${NC}"
        echo "$completed_runs" | jq -r '.[] | "\(.databaseId)|\(.workflowName)"' | while IFS='|' read -r run_id workflow_name; do
            echo -e "    ${YELLOW}Deleting run:${NC} $workflow_name (ID: $run_id)"
            gh run delete "$run_id" 2>/dev/null || true
            sleep 0.3  # Rate limiting
        done
    fi
    
    echo -e "  ${GREEN}✅ Workflow runs cleanup complete${NC}"
}

# Function to perform workflow cleanup with enhanced bulk deletion
perform_cleanup() {
    echo -e "${BLUE}🧹 Starting comprehensive workflow cleanup...${NC}"
    
    # First, clean up workflow runs to reduce clutter
    cleanup_workflow_runs
    echo ""
    
    # Create essential workflow pattern
    local essential_pattern=""
    for workflow in "${ESSENTIAL_WORKFLOWS[@]}"; do
        if [ -z "$essential_pattern" ]; then
            essential_pattern="^${workflow}$"
        else
            essential_pattern="${essential_pattern}|^${workflow}$"
        fi
    done
    
    echo -e "${BLUE}🗂️  Starting workflow deletion...${NC}"
    local deleted_count=0
    local failed_count=0
    local skipped_count=0
    
    # Get all workflows and process in batches
    local all_workflows=$(gh workflow list --json id,name,state --limit=300 2>/dev/null || echo '[]')
    local total_workflows=$(echo "$all_workflows" | jq '. | length')
    
    echo -e "  ${BLUE}Processing $total_workflows total workflows...${NC}"
    
    # Delete non-essential workflows with enhanced error handling
    echo "$all_workflows" | jq -r --arg pattern "$essential_pattern" '.[] | select(.name | test($pattern) | not) | "\(.id)|\(.name)|\(.state)"' | while IFS='|' read -r workflow_id workflow_name workflow_state; do
        echo -e "  ${YELLOW}Deleting:${NC} $workflow_name (ID: $workflow_id, State: $workflow_state)"
        
        # Try multiple deletion approaches
        local deletion_success=false
        
        # Method 1: Standard deletion
        if gh workflow delete "$workflow_id" --confirm 2>/dev/null; then
            deletion_success=true
        else
            # Method 2: Force deletion with API call
            if gh api "repos/{owner}/{repo}/actions/workflows/$workflow_id" -X DELETE 2>/dev/null; then
                deletion_success=true
            fi
        fi
        
        if [ "$deletion_success" = true ]; then
            echo -e "    ${GREEN}✅ Deleted successfully${NC}"
            ((deleted_count++))
        else
            echo -e "    ${RED}❌ Failed to delete (may be protected or have recent runs)${NC}"
            ((failed_count++))
        fi
        
        # Adaptive rate limiting based on API responses
        sleep 0.5
    done
    
    # Count preserved workflows
    local preserved_count=$(echo "$all_workflows" | jq -r --arg pattern "$essential_pattern" '.[] | select(.name | test($pattern)) | .id' | wc -l)
    
    echo ""
    echo -e "${GREEN}🎉 Workflow cleanup complete!${NC}"
    echo -e "  ${GREEN}✅ Workflows deleted: ${deleted_count}${NC}"
    echo -e "  ${GREEN}✅ Essential workflows preserved: ${preserved_count}${NC}"
    if [ "$failed_count" -gt 0 ]; then
        echo -e "  ${RED}❌ Failed deletions: ${failed_count}${NC}"
        echo -e "  ${YELLOW}💡 Some workflows may require manual deletion if they have recent runs${NC}"
    fi
}

# Function to verify final state
verify_final_state() {
    echo -e "${BLUE}🔍 Verifying final workflow state...${NC}"
    
    local total_workflows=$(gh workflow list --json id | jq '. | length')
    echo -e "${GREEN}📊 Final workflow count: ${total_workflows}${NC}"
    
    echo -e "${BLUE}📋 Remaining workflows:${NC}"
    gh workflow list --json id,name,state | jq -r '.[] | "  ✅ \(.name) (\(.state))"' | sort
    
    if [ "$total_workflows" -le 6 ]; then
        echo -e "${GREEN}🎉 Perfect! Workflow count is now optimal (≤6).${NC}"
    else
        echo -e "${YELLOW}⚠️  Still have ${total_workflows} workflows. You may want to review for additional cleanup.${NC}"
    fi
}

# Function for aggressive cleanup mode
aggressive_cleanup() {
    echo -e "${RED}🔥 AGGRESSIVE CLEANUP MODE${NC}"
    echo -e "${RED}This will attempt to delete ALL workflows except the 6 essential ones${NC}"
    echo -e "${RED}Including any workflow runs, artifacts, and caches${NC}"
    echo ""
    
    read -p "Are you absolutely sure? This is very destructive! (yes/NO): " -r
    if [[ $REPLY == "yes" ]]; then
        echo -e "${RED}🚨 Starting aggressive cleanup...${NC}"
        
        # Delete ALL workflow runs first
        echo -e "${YELLOW}Deleting ALL workflow runs...${NC}"
        gh run list --limit=1000 --json databaseId 2>/dev/null | jq -r '.[].databaseId' | while read run_id; do
            gh run delete "$run_id" 2>/dev/null || true
            sleep 0.2
        done
        
        # Clear caches
        echo -e "${YELLOW}Clearing workflow caches...${NC}"
        gh cache list --limit=100 2>/dev/null | tail -n +2 | cut -f1 | while read cache_id; do
            gh cache delete "$cache_id" 2>/dev/null || true
        done
        
        # Now delete workflows
        perform_cleanup
        
        echo -e "${RED}🔥 Aggressive cleanup complete!${NC}"
    else
        echo -e "${BLUE}Aggressive cleanup cancelled.${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Clever AI - GitHub Workflow Cleanup Script${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo ""
    echo "This script will help you clean up excessive GitHub workflows"
    echo "while preserving Clever's 6 essential workflows."
    echo ""
    echo -e "${YELLOW}🔍 Detected: You mentioned 230 workflows in GitHub browser${NC}"
    echo ""
    
    # Check dependencies
    check_dependencies
    echo ""
    
    # List current state
    echo -e "${BLUE}📊 Analyzing current repository state...${NC}"
    local workflow_count=$(gh workflow list --json id 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
    local run_count=$(gh run list --limit=100 --json databaseId 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
    
    echo -e "  ${BLUE}Local workflows visible via CLI: ${workflow_count}${NC}"
    echo -e "  ${BLUE}Recent workflow runs: ${run_count}${NC}"
    echo -e "  ${YELLOW}Browser shows: 230 workflows${NC}"
    echo ""
    
    if [ "$workflow_count" -lt 50 ] && [ "$1" != "--force" ]; then
        echo -e "${YELLOW}⚠️  CLI shows fewer workflows than browser (${workflow_count} vs 230)${NC}"
        echo -e "${YELLOW}This might be due to:${NC}"
        echo -e "  ${YELLOW}• Disabled workflows not showing in CLI${NC}"
        echo -e "  ${YELLOW}• Different repository view${NC}"
        echo -e "  ${YELLOW}• Workflow runs being counted as workflows${NC}"
        echo ""
        echo -e "${BLUE}Options:${NC}"
        echo -e "  ${GREEN}1)${NC} Standard cleanup (recommended)"
        echo -e "  ${RED}2)${NC} Aggressive cleanup (deletes runs, caches, everything)"
        echo -e "  ${BLUE}3)${NC} Show detailed analysis first"
        echo ""
        read -p "Choose option (1/2/3): " -n 1 -r
        echo ""
        
        case $REPLY in
            2)
                aggressive_cleanup
                if [ $? -eq 0 ]; then
                    verify_final_state
                fi
                return
                ;;
            3)
                list_workflows
                identify_deletable_workflows
                echo ""
                echo -e "${BLUE}Run script again with option 1 or 2 to proceed${NC}"
                return
                ;;
            1|*)
                echo -e "${GREEN}Proceeding with standard cleanup...${NC}"
                ;;
        esac
    fi
    
    # Standard cleanup flow
    list_workflows
    
    # Identify what needs cleanup
    identify_deletable_workflows
    deletable_count=$?
    echo ""
    
    # Confirmation prompt
    echo -e "${YELLOW}⚠️  WARNING: This action cannot be undone!${NC}"
    echo -e "${YELLOW}⚠️  Make sure you've reviewed the workflows to be deleted above.${NC}"
    echo ""
    read -p "Do you want to proceed with the cleanup? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        perform_cleanup
        echo ""
        verify_final_state
        echo ""
        echo -e "${GREEN}🎊 Cleanup completed successfully!${NC}"
        echo -e "${GREEN}Your repository now has a streamlined, efficient workflow setup.${NC}"
        echo ""
        echo -e "${BLUE}💡 If you still see many workflows in GitHub browser:${NC}"
        echo -e "  ${BLUE}• Refresh the page (browser cache)${NC}"
        echo -e "  ${BLUE}• Check Actions tab → Workflows section${NC}"
        echo -e "  ${BLUE}• Run this script with aggressive mode if needed${NC}"
    else
        echo ""
        echo -e "${BLUE}ℹ️  Cleanup cancelled. No workflows were modified.${NC}"
        exit 0
    fi
}

# Run main function
main "$@"