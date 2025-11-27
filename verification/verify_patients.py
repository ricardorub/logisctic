from playwright.sync_api import sync_playwright

def verify_patients_combobox():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Login
        page.goto("http://localhost:5000/auth/login")
        page.fill("input[name='email']", "admin@healthmonitor.com")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")

        # Navigate to patients page
        page.goto("http://localhost:5000/patients/patients")

        # Take screenshot of the table area
        page.screenshot(path="verification/patients_page.png", full_page=True)

        # Check if the select element exists in the table
        selects = page.locator("#patientsTable select.form-select")
        count = selects.count()
        print(f"Select elements found: {count}")

        if count > 0:
            # Change the value of the first select
            select = selects.first
            current_value = select.input_value()
            print(f"Current value: {current_value}")

            new_value = 'advertencia' if current_value != 'advertencia' else 'normal'
            select.select_option(new_value)

            # Wait for reload
            page.wait_for_load_state('networkidle')

            # Verify persistence
            select = page.locator("#patientsTable select.form-select").first
            print(f"New value: {select.input_value()}")

            page.screenshot(path="verification/patients_page_updated.png", full_page=True)
        else:
             print("No patients found or selects missing.")

        browser.close()

if __name__ == "__main__":
    verify_patients_combobox()
