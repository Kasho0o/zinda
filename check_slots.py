from seleniumbase import BaseCase

class SlotChecker(BaseCase):
    def test_slot_check(self):
        self.open("https://icp.administracionelectronica.gob.es/icpplustiem/index.html?mDes=N")
        self.wait_for_ready_state_complete()
        self.assert_title_contains("Cita Previa")
        self.assert_text("No hay citas disponibles", by="text", timeout=10)
        # Extract session IDs from headers
        icpplus = self.get_attribute("#some-hidden-field", "value")  # If IDs are in HTML
        # Or extract from JavaScript (if in JS variables)
        icpplus = self.execute_script("return window.ICPPLUS")  # If in JS
        jsessionid = self.execute_script("return window.JSESSIONID")
        print(f"ICPPLUS: {icpplus}, JSESSIONID: {jsessionid}")
        self.set_text("#icpplus-field", icpplus)  # If you need to input IDs
        self.set_text("#jsessionid-field", jsessionid)
        self.click("button[type='submit']")
        self.wait_for_ready_state_complete()
        self.assert_text("Seleccione" or "Confirmar", by="text", timeout=10)
        self.save_screenshot("screenshot.png")
