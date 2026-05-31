document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const menuBtn = document.getElementById('menuBtn');
    const mobileMenu = document.getElementById('mobileMenu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Contact Form Logic (if present)
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const lang = document.documentElement.lang;
            let message = "Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.";
            if (lang === 'uz') message = "Rahmat! Sizning so'rovingiz qabul qilindi. Tez orada siz bilan bog'lanamiz.";
            if (lang === 'en') message = "Thank you! Your request has been received. We will contact you shortly.";

            alert(message);
            this.reset();
        });
    }

    // Product auto-selection from URL
    const urlParams = new URLSearchParams(window.location.search);
    const product = urlParams.get('product');
    const select = document.querySelector('select');
    if (product && select) {
        // Simple mapping or matching
        for (let option of select.options) {
            if (option.value.toLowerCase().includes(product.toLowerCase()) ||
                option.text.toLowerCase().includes(product.toLowerCase())) {
                option.selected = true;
                break;
            }
        }
    }
});
