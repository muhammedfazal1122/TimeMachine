// (function ($) {
//     "use strict";

//     // Initialize the chart data with empty arrays
//     var initialData = {
//         labels: [],
//         datasets: [
//             {
//                 label: 'Sales',
//                 tension: 0.2,
//                 fill: true,
//                 backgroundColor: 'rgba(44, 120, 220, 0.2)',
//                 borderColor: 'rgba(44, 120, 220)',
//                 data: []
//             }
//         ]
//     };

//     var ctx = document.getElementById('myChart').getContext('2d');
//     var chart = new Chart(ctx, {
//         type: 'line',
//         data: initialData,
//         options: {
//             plugins: {
//                 legend: {
//                     labels: {
//                         usePointStyle: true,
//                     },
//                 }
//             },
//             scales: {
//                 y: {
//                     suggestedMin: 0, 
//                     suggestedMax: 10, 
//                     beginAtZero: true, 
//                 }
//             }
//         }
//     });

//     function updateChart(newData) {
//         chart.data.labels = Object.keys(newData);
//         chart.data.datasets[0].data = Object.values(newData);
//         chart.update();
//     }

//     function fetchData(url, successCallback) {
//         $.ajax({
//             type: 'POST',
//             url: url,
//             success: successCallback,
//             error: function (error) {
//                 console.log('Error:', error);
//             }
//         });
//     }

//     // Make an initial AJAX request to get the default data (monthly data)
//     fetchData('/admin/fetchData/month', function (monthlyData) {
//         updateChart(monthlyData);
//     });

//     $('#dailyButton').on('click', function () {
//         fetchData('/admin/fetchData/week', function (dailyData) {
//             updateChart(dailyData);
//         });
//     });

//     $('#MonthlyButton').on('click', function () {
//         fetchData('/admin/fetchData/month', function (monthlyData) {
//             updateChart(monthlyData);
//         });
//     });

//     $('#YearlyButton').on('click', function () {
//         fetchData('/admin/fetchData/year', function (yearlyData) {
//             updateChart(yearlyData);
//         });
//     });
// })(jQuery);



async function getSalesReport() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: 'http://127.0.0.1:8000/orders/sales-report',
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
                            label: 'Weekly Sales',
                            data: weeklySales,
                            backgroundColor: 'rgba(44, 120, 220, 0.2)',
                            borderColor: 'rgba(44, 120, 220)',
                        },
                        {
                            label: 'Monthly Sales',
                            data: monthlySales,
                            backgroundColor: 'rgba(4, 209, 130, 0.2)',
                            borderColor: 'rgb(4, 209, 130)',
                        },
                        {
                            label: 'Yearly Sales',
                            data: yearlySales,
                            backgroundColor: 'rgba(380, 200, 230, 0.2)',
                            borderColor: 'rgb(380, 200, 230)',
                        }
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