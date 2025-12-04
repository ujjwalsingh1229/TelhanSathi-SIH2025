"""
Seed script to populate Scheme table with government subsidies and schemes data.
Run this after migrations: python seed_schemes.py
"""
import json
from extensions import db
from models import Scheme
from app import app

def seed_schemes():
    """Add sample schemes and subsidies to the database"""
    
    schemes_data = [
        {
            'scheme_code': 'pmkisan',
            'name': 'PM-KISAN Samman Nidhi',
            'description': 'A central sector scheme providing income support to all landholding farmer families across the country to supplement their financial needs. The fund is directly transferred to the bank accounts of the beneficiaries.',
            'scheme_type': 'subsidy',
            'focus_area': 'Income Support',
            'focus_color': '#fbc02d',
            'benefit_amount': '₹6,000/year (3 installments)',
            'eligibility_criteria': 'Landholding Farmer Families with valid land records',
            'apply_steps': [
                'Visit the official PM-KISAN portal (pmkisan.gov.in)',
                'Click on "New Farmer Registration"',
                'Enter Aadhaar number and captcha',
                'Fill in personal and bank details carefully',
                'Submit the application and track the status'
            ],
            'external_link': 'https://pmkisan.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Aadhaar Card', 'Land ownership proof', 'Bank Account details']
        },
        {
            'scheme_code': 'nmeo',
            'name': 'NMEO Oilseed Program',
            'description': 'National Mission on Edible Oils (NMEO) provides financial assistance for popularizing new oilseed crops. Benefits include free seed kits, input subsidies, and technology dissemination.',
            'scheme_type': 'scheme',
            'focus_area': 'Crop Switch',
            'focus_color': '#4caf50',
            'benefit_amount': 'Seed Kit + ₹4,000 Incentive',
            'eligibility_criteria': 'Farmers switching to Oilseeds (Mustard, Groundnut, Soybean)',
            'apply_steps': [
                'Contact your local Krishi Vigyan Kendra (KVK)',
                'Submit land documents and application form to District Agriculture Officer',
                'Enroll in the oilseed cultivation program',
                'Receive subsidized seeds and financial incentives'
            ],
            'external_link': 'http://agricoop.nic.in/programmes-schemes-listing/national-mission-on-oilseeds-and-oil-palm-nmoop',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Land proof', 'Farmer ID', 'Application form']
        },
        {
            'scheme_code': 'smam',
            'name': 'SMAM Mechanization Scheme',
            'description': 'Sub-Mission on Agricultural Mechanization (SMAM) helps farmers purchase modern agricultural machinery. Subsidies range from 40% to 50% depending on the equipment type and farmer category.',
            'scheme_type': 'subsidy',
            'focus_area': 'Equipment',
            'focus_color': '#e64a19',
            'benefit_amount': '40-50% Subsidy on Equipment',
            'eligibility_criteria': 'Individual Farmers/FPOs with valid land holdings',
            'apply_steps': [
                'Register on the SMAM portal or state agriculture website',
                'Select the desired machinery and vendor',
                'Submit required documents (land papers, identity proof)',
                'Obtain approval and purchase the equipment'
            ],
            'external_link': 'http://www.smam.nic.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Land papers', 'Identity proof', 'Bank details', 'Quote from vendor']
        },
        {
            'scheme_code': 'pmfby',
            'name': 'PM Fasal Bima Yojana (PMFBY)',
            'description': 'Provides comprehensive insurance coverage against failure of crops, thereby helping in stabilising the income of farmers. Covers yield losses due to non-preventable risks.',
            'scheme_type': 'scheme',
            'focus_area': 'Insurance',
            'focus_color': '#795548',
            'benefit_amount': 'Comprehensive Crop Insurance',
            'eligibility_criteria': 'Loanee and Non-Loanee Farmers growing notified crops',
            'apply_steps': [
                'If you have a crop loan, you are automatically enrolled',
                'For non-loanee farmers, visit a local bank branch or CSC',
                'Fill out the proposal form and pay the specified premium',
                'Ensure policy document is received and stored safely'
            ],
            'external_link': 'https://pmfby.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Crop details', 'Land area proof', 'Insurance premium']
        },
        {
            'scheme_code': 'perdrop',
            'name': 'Per Drop More Crop (Drip/Sprinkler)',
            'description': 'Focuses on maximizing water use efficiency through micro-irrigation (drip and sprinkler systems). Provides substantial subsidy (50% to 80%) to install these systems.',
            'scheme_type': 'subsidy',
            'focus_area': 'Irrigation',
            'focus_color': '#2196f3',
            'benefit_amount': '50-80% Subsidy on Micro Irrigation',
            'eligibility_criteria': 'Farmers adopting Micro Irrigation systems',
            'apply_steps': [
                'Apply online through the state irrigation scheme portal',
                'Submit field survey report and water source details',
                'Wait for field verification by department officials',
                'Install system from approved vendor after sanction'
            ],
            'external_link': 'http://pmksy.gov.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Water source proof', 'Field survey report', 'Vendor quote']
        },
        {
            'scheme_code': 'soilhealth',
            'name': 'Soil Health Card Scheme',
            'description': 'A scheme to provide every farmer a Soil Health Card (SHC) which carries crop-wise recommendations of nutrients and fertilizers required for individual farms, thus optimizing fertilizer use.',
            'scheme_type': 'scheme',
            'focus_area': 'Soil/Fertilizer',
            'focus_color': '#8bc34a',
            'benefit_amount': 'Free Soil Testing & Advisory',
            'eligibility_criteria': 'All Farmers',
            'apply_steps': [
                'Contact the village-level Soil Testing Lab or KVK',
                'Soil samples are collected by officials',
                'Receive the Soil Health Card with fertilizer recommendations',
                'Use recommendations for optimal crop production'
            ],
            'external_link': 'http://soilhealth.dac.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Land proof', 'Aadhar Card']
        },
        {
            'scheme_code': 'aif',
            'name': 'Agri Infrastructure Fund (AIF)',
            'description': 'A financing facility for creation of post-harvest management infrastructure and community farming assets. Provides a 3% interest subvention on loans up to ₹2 crore.',
            'scheme_type': 'subsidy',
            'focus_area': 'Infrastructure',
            'focus_color': '#607d8b',
            'benefit_amount': '3% Interest Subvention on Loans',
            'eligibility_criteria': 'FPOs, PACS, Individual Entrepreneurs with viable projects',
            'apply_steps': [
                'Prepare a detailed project report (DPR)',
                'Approach your bank for the loan',
                'Register the project on the AIF online portal',
                'Interest subvention will be processed after loan disbursement'
            ],
            'external_link': 'https://agriinfra.dac.gov.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Project DPR', 'Bank loan letter', 'Land proof']
        },
        {
            'scheme_code': 'beekeeping',
            'name': 'National Bee-Keeping Mission',
            'description': 'Promotes holistic development of scientific beekeeping to increase productivity and income. Financial assistance is provided for honey bee colonies, bee boxes, and processing units.',
            'scheme_type': 'subsidy',
            'focus_area': 'Allied Sector',
            'focus_color': '#ffc107',
            'benefit_amount': 'Subsidy on Bee Colonies & Hives',
            'eligibility_criteria': 'Farmers/Beekeepers interested in scientific beekeeping',
            'apply_steps': [
                'Contact the National Bee Board (NBB) or local Horticulture Department',
                'Attend mandatory training sessions',
                'Submit a plan for bee colony purchase and farm placement',
                'Receive subsidy after field verification'
            ],
            'external_link': 'http://nbb.gov.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Training certificate', 'Farm details', 'Bank account proof']
        }
    ]

    with app.app_context():
        # Check if schemes already exist
        existing_count = Scheme.query.count()
        if existing_count > 0:
            print(f'Schemes already exist ({existing_count} records). Skipping seed...')
            return

        for scheme_data in schemes_data:
            # Convert lists to JSON strings
            apply_steps = scheme_data.pop('apply_steps')
            required_documents = scheme_data.pop('required_documents')
            
            scheme = Scheme(
                **scheme_data,
                apply_steps=json.dumps(apply_steps),
                required_documents=json.dumps(required_documents)
            )
            
            db.session.add(scheme)
            print(f'Added: {scheme.name}')
        
        db.session.commit()
        print(f'\n✓ Successfully added {len(schemes_data)} schemes to the database!')

if __name__ == '__main__':
    seed_schemes()
