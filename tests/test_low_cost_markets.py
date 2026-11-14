import unittest

from tools.low_cost_markets import allow_places, filter_payload, low_cost_market


class LowCostMarketTests(unittest.TestCase):
    """Postings from India and other low-cost markets pay local rates; drop them at search time."""

    def test_posting_located_in_india_is_dropped(self):
        self.assertEqual(low_cost_market({"location": "Bengaluru, Karnataka, India"}), "India")

    def test_indian_city_without_the_country_is_dropped(self):
        # LinkedIn writes some Indian metros with no country at all.
        self.assertEqual(low_cost_market({"location": "Greater Coimbatore Area"}), "India")
        self.assertEqual(low_cost_market({"location": "Pune City, Maharashtra"}), "India")

    def test_other_low_cost_markets_are_dropped(self):
        self.assertEqual(low_cost_market({"location": "Egypt"}), "Egypt")
        self.assertEqual(low_cost_market({"location": "Tashkent"}), "Uzbekistan")
        self.assertEqual(low_cost_market({"location": "Buenos Aires, Argentina"}), "Argentina")
        self.assertEqual(low_cost_market({"location": "Remote - LATAM"}), "Latin America")

    def test_posting_that_also_names_an_accepted_market_is_kept(self):
        self.assertIsNone(low_cost_market({"location": "Bengaluru, India or Remote (Europe)"}))
        self.assertIsNone(low_cost_market({"location": "India, Poland"}))

    def test_places_sharing_a_low_cost_name_are_kept(self):
        self.assertIsNone(low_cost_market({"location": "Panama City, FL"}))
        self.assertIsNone(low_cost_market({"location": "Kochi, Japan"}))

    def test_us_places_named_like_low_cost_countries_are_kept(self):
        self.assertIsNone(low_cost_market({"location": "Indianapolis, Indiana"}))
        self.assertIsNone(low_cost_market({"location": "Albuquerque, New Mexico"}))
        self.assertIsNone(low_cost_market({"location": "Alexandria, VA"}))

    def test_european_and_worldwide_postings_are_kept(self):
        self.assertIsNone(low_cost_market({"location": "Turin, Piedmont, Italy"}))
        self.assertIsNone(low_cost_market({"location": "Remote"}))
        self.assertIsNone(low_cost_market({"location": None}))

    def test_a_posting_that_also_lists_an_acceptable_location_is_kept(self):
        self.assertIsNone(low_cost_market({"location": "Azerbaijan; Europe; Ukraine"}))
        self.assertIsNone(low_cost_market({"location": "Bengaluru, India", "countries": ["in", "pl"]}))

    def test_every_location_low_cost_is_dropped(self):
        location = "Florianopolis, Santa Catarina, Brasil; Sao Paulo, Sao Paulo, Brasil"
        self.assertEqual(low_cost_market({"location": location}), "Brazil")

    def test_country_codes_decide_when_present(self):
        self.assertEqual(low_cost_market({"location": "Mumbai", "countries": ["in"]}), "India")
        self.assertEqual(low_cost_market({"location": None, "countries": ["ph", "vn"]}), "Philippines")

    def test_himalayas_location_restrictions_decide_when_present(self):
        self.assertEqual(low_cost_market({"location": "Remote (India)", "locationRestrictions": ["India"]}), "India")
        self.assertIsNone(low_cost_market({"location": "Remote (India, Germany)",
                                           "locationRestrictions": ["India", "Germany"]}))

    def test_exempt_places_are_kept_for_evaluation(self):
        # Places listed in profile/allowed_markets.txt reach evaluation instead of being dropped.
        try:
            allow_places(["Atlantis Africa", "Cape Town"])
            self.assertIsNone(low_cost_market({"location": "Cape Town, Western Cape, Atlantis Africa"}))
            self.assertIsNone(low_cost_market({"location": "Atlantis Africa"}))
            self.assertIsNone(low_cost_market({"location": "Remote", "locationRestrictions": ["Atlantis Africa"]}))
        finally:
            allow_places([])
        self.assertEqual(low_cost_market({"location": "Atlantis Africa"}), "Africa")

    def test_the_rest_of_africa_is_still_dropped(self):
        self.assertEqual(low_cost_market({"location": "Nairobi, Kenya"}), "Kenya")
        self.assertEqual(low_cost_market({"location": "Remote - Africa"}), "Africa")
        self.assertEqual(low_cost_market({"location": None, "countries": ["ng", "ke"]}), "Nigeria")
        # Jordan is on neither list: alone it keeps nothing, an exempt code keeps the posting.
        self.assertEqual(low_cost_market({"location": None, "countries": ["jo", "ng"]}), "Nigeria")
        try:
            allow_places(["jo"])
            self.assertIsNone(low_cost_market({"location": None, "countries": ["jo", "ng"]}))
        finally:
            allow_places([])

    def test_unknown_or_bare_remote_locations_do_not_keep_a_low_cost_posting(self):
        # One location missing from the tables (Anguilla, Jordan, Armenia) or a bare "Remote" used to let
        # almost every low-cost posting through. Only an accepted place keeps one.
        self.assertEqual(low_cost_market({"location": "Remote; India"}), "India")
        self.assertEqual(low_cost_market({"locationRestrictions": ["Egypt", "Jordan"]}), "Egypt")
        self.assertEqual(low_cost_market({"countries": ["am", "kg", "kz", "uz"]}), "Kyrgyzstan")
        self.assertEqual(low_cost_market({"locationRestrictions": ["Anguilla", "Argentina", "Aruba", "Bolivia"]}),
                         "Argentina")
        self.assertIsNone(low_cost_market({"countries": ["br", "pt"]}))
        self.assertIsNone(low_cost_market({"locationRestrictions": ["Argentina", "Australia", "Brazil"]}))

    def test_latam_in_the_title_is_dropped(self):
        self.assertEqual(low_cost_market({"title": "Staff Product Engineer, Frontend (LATAM)",
                                          "location": "Remote - Global"}), "Latin America")
        self.assertIsNone(low_cost_market({"title": "Remote Product Designer - Building Africa's Cashless Future",
                                           "location": "Barcelona, Cataluna"}))

    def test_indian_it_services_firms_are_dropped_wherever_the_role_is(self):
        job = {"company": "Tata Consultancy Services", "location": "London Area, United Kingdom"}
        self.assertEqual(low_cost_market(job), "Indian IT services")
        self.assertEqual(low_cost_market({"company": "Accenture in India", "location": "Remote"}), "India")


class FilterPayloadTests(unittest.TestCase):
    def test_filters_a_portal_payload_and_lists_what_it_dropped(self):
        payload = {"total": 2, "results": [
            {"id": "a", "title": "Prompt Engineer", "company": "Acme", "location": "Kochi, India"},
            {"id": "b", "title": "Conversation Designer", "company": "Beta", "location": "Italy"},
        ]}
        filtered = filter_payload(payload)
        self.assertEqual([job["id"] for job in filtered["results"]], ["b"])
        self.assertEqual(filtered["dropped_low_cost"],
                         [{"id": "a", "title": "Prompt Engineer", "company": "Acme",
                           "location": "Kochi, India", "market": "India"}])
        self.assertEqual(filtered["total"], 2)  # the portal's own fields pass through untouched


if __name__ == "__main__":
    unittest.main()
