# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class RndGridApiController(http.Controller):

    @http.route('/api/rndgrid/submit_request', type='json', auth='public', methods=['POST'], csrf=False)
    def create_lead(self, **payload):
        print("payload\n", payload)
        """
        Public endpoint to create a CRM Lead.
        Expects a JSON payload like:
        {
            "mobile": "+1234567890",
            "expected_revenue": 500,
            "description": "Optional notes from the customer",
            "tests": [
                {
                    "material_name": "Silicon Wafer",
                    "sample_type": "thin_film",
                    "is_hazardous": False,
                    "instrument_id": 1,
                    "test_ids": [5, 6]
                }
            ]
        }
        """
        mobile = payload.get('mobile', '').strip()
        print(">>>>>>>>>>>>>", mobile)
        if not mobile:
            return {'status': 'error', 'message': 'Mobile number is required'}

        # Ensure crm module is installed in environment
        if 'crm.lead' not in request.env:
            return {'status': 'error', 'message': 'CRM module is not installed'}

        # Find the partner by mobile
        partner = request.env['res.partner'].sudo().search([('phone', 'ilike', mobile)], limit=1)
        print("partner", partner)

        if not partner:
            return {'status': 'error', 'message': f'No partner found for mobile: {mobile}'}

        # Build the lines for 'crm.lead.rndgrid.test'
        test_lines = []
        for test in payload.get('tests', []):
            test_lines.append((0, 0, {
                'rndgrid_material_name': test.get('material_name'),
                'rndgrid_sample_type': test.get('sample_type'),
                'rndgrid_is_hazardous': test.get('is_hazardous', False),
                'instrument_id': test.get('instrument_id'),
                'test_ids': [(6, 0, test.get('test_ids', []))]
            }))

        # Create the lead
        lead_vals = {
            'name': f'Request from {partner.name}',
            'partner_id': partner.id,
            'expected_revenue': payload.get('expected_revenue', 0.0),
            'description': payload.get('description', ''),
        }

        # Only add tests if the sales_and_crm_customization module is installed (fields exist)
        if 'rndgrid_test_line_ids' in request.env['crm.lead']._fields:
            lead_vals['rndgrid_test_line_ids'] = test_lines

        try:
            lead = request.env['crm.lead'].sudo().create(lead_vals)
            return {
                'status': 'success',
                'lead_id': lead.id,
                'message': 'Lead created successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/rndgrid/instruments', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_instruments(self):
        """
        Public endpoint to get all instruments and their associated tests.
        Returns a JSON array of instruments with 'tests' nested inside.
        """
        try:
            instruments = request.env['rndgrid.instrument'].sudo().search([])
            data = []
            
            for inst in instruments:
                tests = []
                for test in inst.test_ids:
                    tests.append({
                        'id': test.id,
                        'name': test.name
                    })
                
                data.append({
                    'id': inst.id,
                    'name': inst.name,
                    'tests': tests
                })

            return request.make_response(
                json.dumps({'status': 'success', 'data': data}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
