

async function getSalesReport() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: 'http://127.0.0.1:8000/user/sales-report',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                resolve(data);
            },
            error: function(error) {
                reject(error);
            }
        });
    });
}


// })(jQuery);


(function ($) {
    "use strict";

    /*Sale statistics Chart*/
    if ($('#myChart').length) {


        var ctx = document.getElementById('myChart').getContext('2d');


        //getting data
        getSalesReport()
            .then(function(data) {
                console.log(data);
                // Do something with the data
            })
            .catch(function(error) {
                console.error('Error:', error);
            });
        //parsing the data

        
        async function drawChart() {
            const salesData = await getSalesReport();
        
            const ctx = document.getElementById('myChart').getContext('2d');
        
            const productNames = salesData.weekly_sales.map(item => item.product__product_name);
            const weeklySales = salesData.weekly_sales.map(item => item.weekly_sales);
            const monthlySales = salesData.monthly_sales.map(item => item.monthly_sales);
            const yearlySales = salesData.yearly_sales.map(item => item.yearly_sales);
        
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: productNames,
                    datasets: [
                        {
                            label: 'Sales Report',
                            data: weeklySales,
                            backgroundColor: 'rgba(44, 120, 220, 0.2)',
                            borderColor: 'rgba(44, 120, 220)',
                        },
                       
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            labels: {
                                usePointStyle: true,
                            },
                        }
                    }
                }
            });
        }
        
        drawChart();
    
    } //End if


  
    
})(jQuery);

