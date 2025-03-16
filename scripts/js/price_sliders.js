class PriceRangeSlider {
    constructor() {
        // Referencias a elementos
        this.priceMin = document.getElementById('precio_min');
        this.priceMax = document.getElementById('precio_max');
        this.sliderMin = document.getElementById('precio_slider_min');
        this.sliderMax = document.getElementById('precio_slider_max');
        this.sliderTrack = document.querySelector('.slider-track');

        // Configuración
        this.minValue = 0;
        this.maxValue = 10000;
        this.gap = 50;

        // Establecer valores iniciales
        this.priceMin.value = this.minValue;
        this.priceMax.value = this.maxValue;
        this.sliderMin.value = this.minValue;
        this.sliderMax.value = this.maxValue;

        this.initializeEventListeners();
        this.updateSliderValues();
    }

    initializeEventListeners() {
        this.sliderMin.addEventListener('input', () => this.updateSliderMin());
        this.sliderMax.addEventListener('input', () => this.updateSliderMax());
        this.priceMin.addEventListener('change', () => this.updateInputMin());
        this.priceMax.addEventListener('change', () => this.updateInputMax());
    }

    updateSliderMin() {
        let minVal = parseInt(this.sliderMin.value);
        let maxVal = parseInt(this.sliderMax.value);

        if (maxVal - minVal < this.gap) {
            minVal = maxVal - this.gap;
            this.sliderMin.value = minVal;
        }

        this.priceMin.value = minVal;
        this.updateSliderValues();
    }

    updateSliderMax() {
        let minVal = parseInt(this.sliderMin.value);
        let maxVal = parseInt(this.sliderMax.value);

        if (maxVal - minVal < this.gap) {
            maxVal = minVal + this.gap;
            this.sliderMax.value = maxVal;
        }

        this.priceMax.value = maxVal;
        this.updateSliderValues();
    }

    updateInputMin() {
        let minVal = parseInt(this.priceMin.value);
        let maxVal = parseInt(this.priceMax.value);

        if (minVal < 0) minVal = 0;
        if (minVal > maxVal - this.gap) minVal = maxVal - this.gap;

        this.priceMin.value = minVal;
        this.sliderMin.value = minVal;
        this.updateSliderValues();
    }

    updateInputMax() {
        let minVal = parseInt(this.priceMin.value);
        let maxVal = parseInt(this.priceMax.value);

        if (maxVal > 10000) maxVal = 10000;
        if (maxVal < minVal + this.gap) maxVal = minVal + this.gap;

        this.priceMax.value = maxVal;
        this.sliderMax.value = maxVal;
        this.updateSliderValues();
    }

    updateSliderValues() {
        const minVal = parseInt(this.sliderMin.value);
        const maxVal = parseInt(this.sliderMax.value);

        // Usar this.minValue en lugar de 0 implícitamente
        const percent1 = ((minVal - this.minValue) / (this.maxValue - this.minValue)) * 100;
        const percent2 = ((maxVal - this.minValue) / (this.maxValue - this.minValue)) * 100;

        this.sliderTrack.style.background = `linear-gradient(to right, 
            #ddd ${percent1}%, 
            #2196F3 ${percent1}%, 
            #2196F3 ${percent2}%, 
            #ddd ${percent2}%)`;
    }
}
// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.priceRangeSlider = new PriceRangeSlider();
});