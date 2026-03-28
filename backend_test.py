import requests
import sys
from datetime import datetime
import json

class DemandPlanningAPITester:
    def __init__(self, base_url="https://build-dash-26.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_size": len(response.text) if response.text else 0
            }

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    result["response_data"] = response_data
                    
                    # Log data structure info
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response: Dict with keys: {list(response_data.keys())}")
                        
                except json.JSONDecodeError:
                    print(f"   Response: Non-JSON content ({len(response.text)} chars)")
                    result["response_data"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    result["error_data"] = error_data
                    print(f"   Error: {error_data}")
                except:
                    result["error_data"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"   Error: {response.text[:200]}")

            self.test_results.append(result)
            return success, response.json() if success and response.text else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": "TIMEOUT",
                "success": False,
                "error": "Request timeout"
            }
            self.test_results.append(result)
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": "ERROR",
                "success": False,
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_all_skus(self):
        """Test getting all SKUs"""
        success, response = self.run_test(
            "Get All SKUs",
            "GET",
            "skus",
            200
        )
        
        if success and response:
            # Validate response structure
            if isinstance(response, list) and len(response) > 0:
                first_sku = response[0]
                if 'item_id' in first_sku:
                    print(f"   ✅ Found {len(response)} SKUs, first: {first_sku['item_id']}")
                    return response  # Return SKUs for further testing
                else:
                    print(f"   ⚠️  SKU structure missing 'item_id' field")
            else:
                print(f"   ⚠️  Empty or invalid SKU list")
        
        return [] if success else None

    def test_home_data(self):
        """Test getting home page aggregated data"""
        success, response = self.run_test(
            "Get Home Data (52-week chart)",
            "GET",
            "home-data",
            200
        )
        
        if success and response:
            # Validate chart data structure
            chart_data = response.get('chart_data', [])
            if chart_data:
                historical_count = len([d for d in chart_data if d.get('type') == 'historical'])
                forecast_count = len([d for d in chart_data if d.get('type') == 'forecast'])
                print(f"   ✅ Chart data: {historical_count} historical + {forecast_count} forecast points")
                
                # Check for required fields
                sample_point = chart_data[0]
                required_fields = ['timestamp', 'units_sold', 'type']
                missing_fields = [field for field in required_fields if field not in sample_point]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in chart data: {missing_fields}")
                else:
                    print(f"   ✅ Chart data structure is valid")
            else:
                print(f"   ⚠️  No chart data found")
        
        return success

    def test_alerts(self):
        """Test getting forecast alerts"""
        success, response = self.run_test(
            "Get Forecast Alerts",
            "GET",
            "alerts",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   ✅ Found {len(response)} alerts")
                
                # Validate alert structure
                if len(response) > 0:
                    sample_alert = response[0]
                    required_fields = ['item_id', 'severity', 'message', 'deviation_percent']
                    missing_fields = [field for field in required_fields if field not in sample_alert]
                    if missing_fields:
                        print(f"   ⚠️  Missing fields in alert: {missing_fields}")
                    else:
                        print(f"   ✅ Alert structure is valid")
                        print(f"   Sample alert: {sample_alert['item_id']} - {sample_alert['severity']} priority")
            else:
                print(f"   ⚠️  Alerts response is not a list")
        
        return success

    def test_sku_detail(self, item_id):
        """Test getting SKU detail data"""
        success, response = self.run_test(
            f"Get SKU Detail ({item_id})",
            "GET",
            f"sku/{item_id}",
            200
        )
        
        if success and response:
            # Validate SKU detail structure
            required_fields = ['item_id', 'chart_data']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields in SKU detail: {missing_fields}")
            else:
                chart_data = response.get('chart_data', [])
                historical_count = len([d for d in chart_data if d.get('type') == 'historical'])
                forecast_count = len([d for d in chart_data if d.get('type') == 'forecast'])
                print(f"   ✅ SKU chart data: {historical_count} historical + {forecast_count} forecast points")
        
        return success

    def test_demand_drivers(self, item_id):
        """Test getting demand drivers for SKU"""
        success, response = self.run_test(
            f"Get Demand Drivers ({item_id})",
            "GET",
            f"sku/{item_id}/demand-drivers",
            200
        )
        
        if success and response:
            # Validate demand drivers structure
            demand_drivers = response.get('demand_drivers', [])
            if demand_drivers:
                historical_count = len([d for d in demand_drivers if d.get('type') == 'historical'])
                forecast_count = len([d for d in demand_drivers if d.get('type') == 'forecast'])
                print(f"   ✅ Demand drivers: {historical_count} historical + {forecast_count} forecast points")
                
                # Check for required fields
                sample_driver = demand_drivers[0]
                required_fields = ['timestamp', 'avg_unit_price', 'cust_instock', 'type']
                missing_fields = [field for field in required_fields if field not in sample_driver]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in demand driver: {missing_fields}")
                else:
                    print(f"   ✅ Demand driver structure is valid")
            else:
                print(f"   ⚠️  No demand drivers found")
        
        return success

    def test_invalid_sku(self):
        """Test getting data for non-existent SKU"""
        success, response = self.run_test(
            "Get Invalid SKU Detail",
            "GET",
            "sku/INVALID_SKU_ID",
            404
        )
        return success

def main():
    print("🚀 Starting Demand Planning Dashboard API Tests")
    print("=" * 60)
    
    # Setup
    tester = DemandPlanningAPITester()
    
    # Test basic endpoints
    print("\n📋 Testing Basic Endpoints...")
    tester.test_root_endpoint()
    
    # Test SKU list
    print("\n📦 Testing SKU Management...")
    skus = tester.test_get_all_skus()
    
    # Test home data
    print("\n🏠 Testing Home Page Data...")
    tester.test_home_data()
    
    # Test alerts
    print("\n🚨 Testing Forecast Alerts...")
    tester.test_alerts()
    
    # Test SKU detail and demand drivers (if we have SKUs)
    if skus and len(skus) > 0:
        print("\n📊 Testing SKU Detail Pages...")
        # Test first few SKUs
        test_skus = skus[:3]  # Test first 3 SKUs
        
        for sku in test_skus:
            item_id = sku['item_id']
            tester.test_sku_detail(item_id)
            tester.test_demand_drivers(item_id)
    
    # Test error handling
    print("\n❌ Testing Error Handling...")
    tester.test_invalid_sku()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    # Calculate success rate
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Print failed tests
    failed_tests = [test for test in tester.test_results if not test['success']]
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test['test_name']}: {test.get('actual_status', 'Unknown')} - {test.get('error', 'No error details')}")
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': success_rate,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to /app/backend_test_results.json")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())