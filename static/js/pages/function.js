$(document).ready(function() {
    let filter_object = {}; // Define filter_object

    function updateRange(value) {
        filter_object.min_price = value;
        $('#range').val(value); // Update the range input value
        $('#max_price').val(value); // Update the max_price input value
    }

    let prevPrice = $("#max_price").val(); // Store the previous input value

    $('.filter-checkbox, #price-filter-btn').on('click', function() {
        let min_price = $('#max_price').attr('min');
        let max_price = $('#max_price').val();

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        console.log('The min price is', min_price);
        console.log('The max price is', max_price);

        // Perform filtering or other actions with the filter_object
        // ...

        // Send AJAX request to the Django view
        $.ajax({
            type: 'GET',
            url: '{% url "filter_product" %}',  // Update with your URL
            data: filter_object,
            success: function(response) {
                $('#product-listing').html(response.data);
                updateRange(max_price); // Update the range input after filtering
            },
            error: function(error) {
                console.log('An error occurred:', error);
            }
        });
    });

    $("#max_price").on("blur", function() {
        let min_price = parseInt($(this).attr("min"));
        let max_price = parseInt($(this).attr("max"));
        let current_price = parseInt($(this).val());

        if (current_price !== prevPrice) { // Check if the value actually changed
            prevPrice = current_price; // Update the previous value
            if (current_price < min_price || current_price > max_price) {
                console.log('The current price is', current_price);
                console.log('The min price is', min_price);
                console.log('The max price is', max_price);
                let errorMessage = 'The price must be between ₹' + min_price + ' and ₹' + max_price;
                alert(errorMessage);

                $(this).val(min_price);
                updateRange(min_price); // Update the range input as well
                $(this).focus();
            }
        }
    });
});
