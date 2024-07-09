$(document).ready(function() {
    // Function to update cart counter
    function updateCartCounter(counterValue) {
        if (counterValue !== null && !isNaN(counterValue)) {
            $('#cart_counter').html(counterValue);
            if (counterValue === 0) {
                $("#empty-cart").css("display", "block");
            } else {
                $("#empty-cart").css("display", "none");
            }
        }
    }

    // Initialize cart counter on page load
    updateCartCounter(parseInt($('#cart_counter').html()));

    // Function to handle adding to cart
    function addToCart(product_id, url) {
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                console.log(response);
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function() {
                        window.location = '/account/login/';
                    });
                } else if (response.status == 'Failed') {
                    swal(response.message, '', 'error');
                } else if (response.status == 'Success') {
                    updateCartCounter(response.cart_counter['cart_count']);
                    $('#qty-' + product_id).html(response.qty);
                    // Do not update the cart amount
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', xhr.responseText);
                var response = xhr.responseJSON;
                if (response && response.status == 'Failed' && response.message == 'Maximum limit reached for this product!') {
                    swal({
                        title: 'Maximum Limit Reached',
                        text: 'You have reached the maximum limit for this product.',
                        icon: 'warning',
                        button: 'OK'
                    });
                } else {
                    alert('Error: ' + (response ? response.message : 'Unknown error'));
                }
            }
        });
    }

    // Handle click on add to cart button
    $('.add_to_cart').on('click', function(e) {
        e.preventDefault();
        let product_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');
        addToCart(product_id, url);
    });

    // Handle click on decrease cart button
    $('.decrease_cart').on('click', function(e) {
        e.preventDefault();
        let product_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');
        decreaseCart(product_id, url);
    });

        // DELETE CART ITEM
        $('.delete_cart').on('click', function(e){
            e.preventDefault();
            
            cart_id = $(this).attr('data-id');
            url = $(this).attr('data-url');
            
            
            $.ajax({
                type: 'GET',
                url: url,
                success: function(response){
                    console.log(response)
                    if(response.status == 'Failed'){
                        swal(response.message, '', 'error')
                    }else{
                        $('#cart_counter').html(response.cart_counter['cart_count']);
                        swal({
                            title: response.status,
                            text: response.message,
                            icon: "success",
                            timer: 2000, // Show the swal message for 2 seconds
                            buttons: false
                        }).then(() => {
                            // Redirect to the cart page after 2 seconds
                            window.location.href = response.redirect_url;
                        });
    
                        applyCartAmounts(
                            response.cart_amount['subtotal'],
                            response.cart_amount['tax_dict'],
                            response.cart_amount['grand_total']
                        )
    
                        removeCartItem(0, cart_id);
                        checkEmptyCart();
                    } 
                }
            })
        })

    // Function to handle decreasing cart
    function decreaseCart(product_id, url) {
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                console.log(response);
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function() {
                        window.location.href = '/account/login';
                    });
                } else if (response.status == 'Failed') {
                    swal(response.message, '', 'error');
                } else if (response.status == 'Success') {
                    updateCartCounter(response.cart_counter['cart_count']);
                    $('#qty-' + product_id).html(response.qty);
                    // Do not update the cart amount

                    if (window.location.pathname == '/cart/') {
                        removeCartItem(response.qty, product_id);
                        checkEmptyCart();
                    }
                }
            },
            error: function(xhr, status, error) {
                var response = xhr.responseJSON;
                alert('Error: ' + response.message);
            }
        });
    }

    // Function to handle deleting cart item
    function deleteCartItem(cart_id, url) {
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                console.log(response)
                if (response.status == 'Failed') {
                    swal(response.message, '', 'error')
                } else {
                    updateCartCounter(response.cart_counter['cart_count']);
                    swal(response.status, response.message, "success")

                    removeCartItem(0, cart_id);
                    checkEmptyCart();
                }
            }
        });
    }

    // Function to remove cart item from UI
    function removeCartItem(cartItemQty, cart_id) {
        if (cartItemQty <= 0) {
            $("#cart-item-" + cart_id).remove();
        }
    }

    // Function to check if cart is empty and update UI
    function checkEmptyCart() {
        var cart_counter = parseInt($('#cart_counter').html());
        if (cart_counter === 0) {
            $("#empty-cart").css("display", "block");
        } else {
            $("#empty-cart").css("display", "none");
        }
    }

    // apply cart amounts
    function applyCartAmounts(subtotal, tax_dict, grand_total) {
        if (window.location.pathname === '/shop/cart/') {
            $('#subtotal').html(subtotal);
            $('#total').html(grand_total);
            console.log(tax_dict)
        }
    }
});
