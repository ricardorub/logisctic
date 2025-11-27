from playwright.sync_api import sync_playwright

def verify_stats_combobox():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Login first (assuming login is required or we can access stats directly if auth is bypassed or handled)
        # Based on routes, login_required is used.
        # I'll try to login as admin
        page.goto("http://localhost:5000/auth/login")
        page.fill("input[name='email']", "admin@healthmonitor.com")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")

        # Navigate to stats page
        page.goto("http://localhost:5000/monitor/stats")

        # Take screenshot of the table area
        page.screenshot(path="verification/stats_page.png", full_page=True)

        # Check if the select element exists
        select_exists = page.locator("select.status-select").count() > 0
        print(f"Select element exists: {select_exists}")

        if select_exists:
            # Try to change the value
            # Assuming there is at least one patient in critical/warning state to show up in the table
            # If not, the table might be empty.

            # Let's check if there are rows in the table
            rows = page.locator("table tbody tr")
            if rows.count() > 0:
                 # Check for "No hay pacientes" message
                 first_row_text = rows.first.inner_text()
                 if "No hay pacientes" in first_row_text:
                     print("No patients to update.")
                 else:
                     # Select the first select element
                     select = page.locator("select.status-select").first
                     # Change value to 'normal' or something else
                     current_value = select.input_value()
                     print(f"Current value: {current_value}")

                     new_value = 'advertencia' if current_value != 'advertencia' else 'peligro'
                     select.select_option(new_value)

                     # Wait for reload
                     page.wait_for_load_state('networkidle')

                     # Verify value persisted
                     select = page.locator("select.status-select").first
                     print(f"New value: {select.input_value()}")

                     page.screenshot(path="verification/stats_page_updated.png", full_page=True)
            else:
                print("No rows found in table.")

        browser.close()

if __name__ == "__main__":
    verify_stats_combobox()
