/** @odoo-module **/

import { Component } from "@odoo/owl";

// Terminology replacements mapping
const TERM_REPLACEMENTS = {
    'Company': 'Ministry',
    'Companies': 'Ministries',
    'Allowed Companies': 'Allowed Ministries',
    'My Companies': 'My Ministries',
    'Switch Company': 'Switch Ministry',
    'Current Company': 'Current Ministry',
    'Parent Company': 'Parent Ministry',
    'Child Companies': 'Child Ministries',
    'Company Name': 'Ministry Name',
    'Company Settings': 'Ministry Settings',
    'Users & Companies': 'Users & Ministries',
    'User & Companies': 'Users & Ministries',
};

// Function to replace company-related terms
function replaceCompanyTerms(text) {
    if (typeof text !== 'string') return text;
    
    let result = text;
    for (const [oldTerm, newTerm] of Object.entries(TERM_REPLACEMENTS)) {
        const regex = new RegExp('\\b' + oldTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'g');
        result = result.replace(regex, newTerm);
    }
    
    // Also handle HTML entity version
    result = result.replace(/Users\s*&\s*Companies/gi, 'Users & Ministries');
    
    return result;
}

// DOM replacement function
function replaceInDOM() {
    const selectors = [
        'label',
        '.o_form_label',
        '.o_field_label',
        'th',
        '.o_list_header',
        '.breadcrumb',
        '.o_control_panel',
        'span.o_menu_brand',
        '.o_menu_sections a',
        '.dropdown-item',
        'button',
        'h1', 'h2', 'h3', 'h4'
    ];
    
    selectors.forEach(selector => {
        try {
            document.querySelectorAll(selector).forEach(element => {
                if (element.childNodes.length > 0) {
                    element.childNodes.forEach(node => {
                        if (node.nodeType === Node.TEXT_NODE && node.nodeValue && node.nodeValue.trim()) {
                            const originalText = node.nodeValue;
                            const replacedText = replaceCompanyTerms(originalText);
                            if (originalText !== replacedText) {
                                node.nodeValue = replacedText;
                            }
                        }
                    });
                }
            });
        } catch (e) {
            // Ignore selector errors
        }
    });
}

// Initialize
let observer;
function initialize() {
    if (!document.body) {
        setTimeout(initialize, 100);
        return;
    }
    
    // Initial replacement
    setTimeout(replaceInDOM, 500);
    
    // Watch for changes
    observer = new MutationObserver(() => {
        setTimeout(replaceInDOM, 100);
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Start when ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}
