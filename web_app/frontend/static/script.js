function updateValue(id) {
            const element = document.getElementById(id);
            const valueElement = document.getElementById(id + '_value');
            if (element && valueElement) {
                valueElement.textContent = Number(element.value).toLocaleString();
            }
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            const sliders = document.querySelectorAll('input[type="range"]');
            sliders.forEach(slider => updateValue(slider.id));

            const form = document.getElementById('diagnosis-form');
            const placeholder = document.getElementById('result-placeholder');
            const spinner = document.getElementById('loading-spinner');
            const resultDisplay = document.getElementById('result-display');

            form.addEventListener('submit', async (event) => {
                event.preventDefault();

                placeholder.classList.add('hidden');
                resultDisplay.classList.add('hidden');
                spinner.classList.remove('hidden');

                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || `Server error: ${response.status}`);
                    }

                    const result = await response.json();
                    
                    displayResult(result);

                } catch (error) {
                    console.error('Prediction failed:', error);
                    displayError(error.message);
                } finally {
                    spinner.classList.add('hidden');
                    resultDisplay.classList.remove('hidden');
                    resultDisplay.classList.add('fade-in');
                }
            });
            
            function displayResult(result) {
                let htmlContent = '';
                if (result.fault_status === 'No Fault Detected') {
                    htmlContent = `
                        <svg class="w-20 h-20 mx-auto text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <h2 class="text-3xl font-bold text-green-400 mt-4">No Fault Detected</h2>
                        <p class="text-slate-300 mt-2">The vehicle's parameters appear to be within normal operating ranges.</p>
                        <p class="text-sm text-slate-400 mt-4 italic">
                            <strong>Note:</strong> For comprehensive vehicle health, regular professional check-ups are always recommended.
                        </p>
                    `;
                } else {
                    htmlContent = `
                        <svg class="w-20 h-20 mx-auto text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <h2 class="text-3xl font-bold text-red-500 mt-4">Fault Detected</h2>
                        <div class="mt-6 space-y-4 w-full">
                            <div class="bg-red-500/20 p-4 rounded-lg border border-red-500/50">
                                <p class="text-xl font-bold text-white">${result.fault_type}</p>
                                <div class="mt-2 grid grid-cols-2 gap-2 text-center">
                                    <div class="bg-slate-700/50 p-2 rounded">
                                        <p class="text-xs text-red-200">Affected Unit</p>
                                        <p class="text-md font-semibold">${result.faulty_unit}</p>
                                    </div>
                                    <div class="bg-slate-700/50 p-2 rounded">
                                        <p class="text-xs text-red-200">Severity (1-10)</p>
                                        <p class="text-lg font-semibold">${result.fault_severity}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <p class="text-slate-300 mt-6">It is recommended to have the vehicle inspected by a professional.</p>
                    `;
                }
                resultDisplay.innerHTML = htmlContent;
            }

            function displayError(errorMessage) {
                 let htmlContent = `
                    <svg class="w-20 h-20 mx-auto text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    <h2 class="text-2xl font-bold text-yellow-400 mt-4">An Error Occurred</h2>
                    <p class="text-slate-300 mt-2">${errorMessage}</p>
                `;
                resultDisplay.innerHTML = htmlContent;
            }
        });