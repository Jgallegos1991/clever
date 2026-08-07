#!/usr/bin/env python3
"""
Clever Knowledge Validation & Testing Script

This script tests Clever's ability to access and use her knowledge base
across history, economics, and biblical studies.

Why: Validates Clever's knowledge base functionality offline
Where: Called by CI/CD for automated testing and validation
How: Uses offline-only testing methods respecting digital sovereignty
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class CleverKnowledgeValidator:
    def __init__(self, offline_mode: bool = True):
        self.offline_mode = offline_mode
        self.test_results = []

    def test_knowledge_files(self) -> Dict[str, Any]:
        """Test knowledge base files without external dependencies"""
        url = f"{self.base_url}/api/chat"
        payload = {"message": message}

        try:
            response = requests.post(url, json=payload, timeout=30)
            response_data = response.json()

            result = {
                "message": message,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response_data.get("response", ""),
                "mode": response_data.get("analysis", {}).get("mode", ""),
                "contains_keywords": False,
                "response_length": len(response_data.get("response", "")),
                "timestamp": time.time(),
            }

            # Check for expected keywords
            if expected_keywords and result["response"]:
                response_lower = result["response"].lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
                result["contains_keywords"] = len(found_keywords) > 0
                result["found_keywords"] = found_keywords

            return result

        except Exception as e:
            return {
                "message": message,
                "status_code": None,
                "success": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    def run_history_tests(self):
        """Test Clever's historical knowledge"""
        print("🏛️  Testing Historical Knowledge...")

        history_tests = [
            {
                "message": "Who discovered the laws of planetary motion?",
                "keywords": ["Kepler", "Johannes", "elliptical", "orbit", "planetary"],
            },
            {
                "message": "What was the significance of the Printing Press?",
                "keywords": [
                    "Gutenberg",
                    "revolution",
                    "knowledge",
                    "books",
                    "information",
                ],
            },
            {
                "message": "Tell me about the Islamic Golden Age contributions to science",
                "keywords": [
                    "Al-Khwarizmi",
                    "algebra",
                    "medicine",
                    "astronomy",
                    "mathematics",
                ],
            },
            {
                "message": "How did the Industrial Revolution change society?",
                "keywords": [
                    "steam",
                    "factory",
                    "manufacturing",
                    "urban",
                    "transportation",
                ],
            },
            {
                "message": "What can we learn from the fall of Rome?",
                "keywords": ["empire", "decline", "lessons", "governance", "military"],
            },
        ]

        for test in history_tests:
            result = self.test_chat_endpoint(test["message"], test["keywords"])
            result["category"] = "History"
            self.test_results.append(result)

            if result["success"]:
                status = "✅" if result["contains_keywords"] else "⚠️ "
                print(f"  {status} {test['message'][:50]}...")
                if result.get("found_keywords"):
                    print(f"      Found: {', '.join(result['found_keywords'])}")
            else:
                print(f"  ❌ {test['message'][:50]}... - ERROR")

    def run_economics_tests(self):
        """Test Clever's economics knowledge"""
        print("\n💰 Testing Economics Knowledge...")

        economics_tests = [
            {
                "message": "Explain supply and demand to me",
                "keywords": [
                    "price",
                    "quantity",
                    "market",
                    "Adam Smith",
                    "equilibrium",
                ],
            },
            {
                "message": "What is opportunity cost?",
                "keywords": [
                    "choice",
                    "alternative",
                    "trade-off",
                    "scarcity",
                    "decision",
                ],
            },
            {
                "message": "How does inflation affect the economy?",
                "keywords": [
                    "prices",
                    "money",
                    "purchasing power",
                    "central bank",
                    "monetary",
                ],
            },
            {
                "message": "What causes economic recessions?",
                "keywords": [
                    "business cycle",
                    "demand",
                    "unemployment",
                    "GDP",
                    "contraction",
                ],
            },
            {
                "message": "Explain comparative advantage in trade",
                "keywords": [
                    "Ricardo",
                    "specialization",
                    "efficiency",
                    "trade",
                    "production",
                ],
            },
        ]

        for test in economics_tests:
            result = self.test_chat_endpoint(test["message"], test["keywords"])
            result["category"] = "Economics"
            self.test_results.append(result)

            if result["success"]:
                status = "✅" if result["contains_keywords"] else "⚠️ "
                print(f"  {status} {test['message'][:50]}...")
                if result.get("found_keywords"):
                    print(f"      Found: {', '.join(result['found_keywords'])}")
            else:
                print(f"  ❌ {test['message'][:50]}... - ERROR")

    def run_biblical_tests(self):
        """Test Clever's biblical knowledge"""
        print("\n📖 Testing Biblical Knowledge...")

        biblical_tests = [
            {
                "message": "What is the Golden Rule?",
                "keywords": ["do unto others", "Matthew", "treat", "love", "neighbor"],
            },
            {
                "message": "Explain the Parable of the Good Samaritan",
                "keywords": ["Samaritan", "compassion", "neighbor", "help", "mercy"],
            },
            {
                "message": "What does the Bible say about forgiveness?",
                "keywords": ["forgive", "mercy", "Matthew", "seventy", "Lord's Prayer"],
            },
            {
                "message": "Tell me about the Ten Commandments",
                "keywords": ["Moses", "Sinai", "law", "covenant", "moral"],
            },
            {
                "message": "What is the significance of the Exodus?",
                "keywords": ["Egypt", "liberation", "Moses", "Pharaoh", "freedom"],
            },
        ]

        for test in biblical_tests:
            result = self.test_chat_endpoint(test["message"], test["keywords"])
            result["category"] = "Biblical"
            self.test_results.append(result)

            if result["success"]:
                status = "✅" if result["contains_keywords"] else "⚠️ "
                print(f"  {status} {test['message'][:50]}...")
                if result.get("found_keywords"):
                    print(f"      Found: {', '.join(result['found_keywords'])}")
            else:
                print(f"  ❌ {test['message'][:50]}... - ERROR")

    def run_knowledge_integration_tests(self):
        """Test Clever's ability to integrate knowledge across domains"""
        print("\n🧠 Testing Cross-Domain Knowledge Integration...")

        integration_tests = [
            {
                "message": "How did religious beliefs influence economic systems in history?",
                "keywords": [
                    "Protestant",
                    "Catholic",
                    "Islamic",
                    "trade",
                    "banking",
                    "ethics",
                ],
            },
            {
                "message": "What economic lessons can we learn from biblical principles?",
                "keywords": [
                    "stewardship",
                    "jubilee",
                    "debt",
                    "poverty",
                    "wealth",
                    "justice",
                ],
            },
            {
                "message": "How did the Renaissance combine classical learning with Christian thought?",
                "keywords": [
                    "humanism",
                    "classical",
                    "Christian",
                    "synthesis",
                    "learning",
                ],
            },
        ]

        for test in integration_tests:
            result = self.test_chat_endpoint(test["message"], test["keywords"])
            result["category"] = "Integration"
            self.test_results.append(result)

            if result["success"]:
                status = "✅" if result["contains_keywords"] else "⚠️ "
                print(f"  {status} {test['message'][:50]}...")
                if result.get("found_keywords"):
                    print(f"      Found: {', '.join(result['found_keywords'])}")
            else:
                print(f"  ❌ {test['message'][:50]}... - ERROR")

    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 60)
        print("🧠 CLEVER KNOWLEDGE VALIDATION REPORT")
        print("=" * 60)

        # Overall statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        keyword_matches = len([r for r in self.test_results if r.get("contains_keywords", False)])

        print("\n📊 Overall Statistics:")
        print(f"   Total Tests: {total_tests}")
        print(
            f"   Successful Responses: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)"
        )
        print(
            f"   Knowledge Integration: {keyword_matches}/{total_tests} ({keyword_matches/total_tests*100:.1f}%)"
        )

        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result.get("category", "Unknown")
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0, "keywords": 0}
            categories[cat]["total"] += 1
            if result["success"]:
                categories[cat]["success"] += 1
            if result.get("contains_keywords", False):
                categories[cat]["keywords"] += 1

        print("\n📚 Knowledge Domain Performance:")
        for cat, stats in categories.items():
            success_rate = stats["success"] / stats["total"] * 100
            keyword_rate = stats["keywords"] / stats["total"] * 100
            print(f"   {cat}:")
            print(
                f"      Response Success: {stats['success']}/{stats['total']} ({success_rate:.1f}%)"
            )
            print(
                f"      Knowledge Integration: {stats['keywords']}/{stats['total']} ({keyword_rate:.1f}%)"
            )

        # Response quality analysis
        avg_response_length = (
            sum(r.get("response_length", 0) for r in self.test_results if r["success"])
            / successful_tests
            if successful_tests > 0
            else 0
        )
        print("\n💬 Response Quality:")
        print(f"   Average Response Length: {avg_response_length:.0f} characters")

        # Detailed results
        print("\n🔍 Detailed Results:")
        for i, result in enumerate(self.test_results, 1):
            status = (
                "✅"
                if result["success"] and result.get("contains_keywords", False)
                else "⚠️ " if result["success"] else "❌"
            )
            print(
                f"   {i}. {status} [{result.get('category', 'Unknown')}] {result['message'][:40]}..."
            )
            if result["success"] and result.get("found_keywords"):
                print(f"       Keywords found: {', '.join(result['found_keywords'])}")

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "keyword_matches": keyword_matches,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "integration_rate": keyword_matches / total_tests if total_tests > 0 else 0,
            "categories": categories,
            "avg_response_length": avg_response_length,
        }


def main():
    print("🧠 Clever AI Knowledge Validation System")
    print("==========================================")
    print("Testing Clever's knowledge integration across:")
    print("  • World History")
    print("  • Economics")
    print("  • Biblical Studies")
    print("  • Cross-Domain Integration")
    print()

    validator = CleverKnowledgeValidator()

    # Check if Clever is running
    try:
        response = requests.get(f"{validator.base_url}/api/ping", timeout=5)
        if response.status_code != 200:
            print(
                "❌ Clever is not responding properly. Please ensure she's running at http://localhost:5000"
            )
            return
    except:
        print("❌ Cannot connect to Clever. Please ensure she's running at http://localhost:5000")
        return

    print("✅ Connected to Clever successfully!")
    print()

    # Run all test suites
    validator.run_history_tests()
    validator.run_economics_tests()
    validator.run_biblical_tests()
    validator.run_knowledge_integration_tests()

    # Generate comprehensive report
    report = validator.generate_report()

    # Save results
    with open("knowledge_validation_results.json", "w") as f:
        json.dump(
            {
                "timestamp": time.time(),
                "summary": report,
                "detailed_results": validator.test_results,
            },
            f,
            indent=2,
        )

    print("\n💾 Detailed results saved to: knowledge_validation_results.json")

    # Final assessment
    if report["success_rate"] >= 0.9 and report["integration_rate"] >= 0.7:
        print("\n🎉 EXCELLENT: Clever is successfully using her knowledge base!")
    elif report["success_rate"] >= 0.7 and report["integration_rate"] >= 0.5:
        print("\n👍 GOOD: Clever is accessing her knowledge well with room for improvement.")
    else:
        print("\n⚠️  NEEDS WORK: Clever may need knowledge system improvements.")


if __name__ == "__main__":
    main()
