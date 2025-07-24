// Setup Wizard Language Override - Immediate execution
console.log("🚀 Setup Wizard Override Script Loading...");

// Function to set language immediately
function setSetupWizardLanguage() {
    console.log("🔧 Attempting to set setup wizard language...");
    
    // Get language from multiple sources
    let lang = localStorage.getItem('lang') || localStorage.getItem('setup_wizard_lang') || getCookie('setup_wizard_lang') || 'vi';
    console.log("📝 Found language:", lang);
    
    // Map to display format
    let displayLang = (lang === 'vi') ? 'Việt' : lang;
    console.log("🎨 Display language:", displayLang);
    
    // Method 1: Set in frappe.wizard.values (if available)
    if (typeof frappe !== 'undefined' && frappe.wizard && frappe.wizard.values) {
        frappe.wizard.values.language = displayLang;
        console.log("✅ Set language in frappe.wizard.values:", displayLang);
    }
    
    // Method 2: Hook into frappe.setup if available
    if (typeof frappe !== 'undefined' && frappe.setup && frappe.setup.on) {
        frappe.setup.on('before_load', function() {
            console.log("🎯 Setup wizard before_load event triggered");
            if (!frappe.wizard) frappe.wizard = {};
            if (!frappe.wizard.values) frappe.wizard.values = {};
            frappe.wizard.values.language = displayLang;
            console.log("✅ Set language in before_load:", displayLang);
        });
    }
    
    // Method 3: Direct DOM manipulation (backup method)
    setTimeout(function() {
        const languageField = document.querySelector('input[data-fieldname="language"]');
        if (languageField) {
            languageField.value = displayLang;
            console.log("✅ Set language via DOM manipulation:", displayLang);
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            languageField.dispatchEvent(event);
        } else {
            console.log("⚠️ Language field not found in DOM");
        }
    }, 1000);
    
    // Method 4: Override the default value in slide settings
    if (typeof frappe !== 'undefined' && frappe.setup && frappe.setup.slides_settings) {
        for (let slide of frappe.setup.slides_settings) {
            if (slide.name === 'welcome' && slide.fields) {
                for (let field of slide.fields) {
                    if (field.fieldname === 'language') {
                        field.default = displayLang;
                        console.log("✅ Override default in slide settings:", displayLang);
                        break;
                    }
                }
                break;
            }
        }
    }
}

// Helper function to get cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Execute immediately
console.log("🚀 Executing setup wizard language override...");
setSetupWizardLanguage();

// Also execute when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setSetupWizardLanguage);
} else {
    setSetupWizardLanguage();
}

// Execute when frappe is ready
if (typeof frappe !== 'undefined') {
    setSetupWizardLanguage();
} else {
    // Wait for frappe to load
    let checkFrappe = setInterval(function() {
        if (typeof frappe !== 'undefined') {
            clearInterval(checkFrappe);
            setSetupWizardLanguage();
        }
    }, 100);
}

console.log("🎉 Setup Wizard Override Script Loaded"); 