function updateMainImage(newImageUrl){
    console.log('Updating main image:', newImageUrl);
    $('#mainProductImageDisplay').attr('src', newImageUrl);
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("categorySelect").addEventListener("change", function() {
        document.getElementById("categoryForm").submit();
    });
})

var selectedSizeId, sizeSelect;

var updateBtns = document.getElementsByClassName('update-cart')

for (i=0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        console.log('button clicked');

        var productId = this.dataset.product
        var action = this.dataset.action
        var sizeSelect = document.getElementById('sizeSelect')
        /*var selectedSizeId = sizeSelect.value*/

        if(sizeSelect){
            selectedSizeId = sizeSelect.value
        }else{
            selectedSizeId;
        }
        
        console.log('productId:', productId, 'Action:', action, 'Selected Size', selectedSizeId)
        console.log('USER: ', user)

        if(user == 'AnonymousUser'){
            addCookieItem(productId, action)
        }else{
            updateUserOrder(productId, action, selectedSizeId)
        }      
    })
}

//ADD onclick="saveOption()" again on product_detail add to order button 
// function saveOption(){
//     var sizeSelect = document.getElementById('sizeSelect')
//     var selectedSizeId = sizeSelect.value

//     localStorage.setItem("selectedSizeId", selectedSizeId)
//     alert('Option saved!')
// }

function updateUserOrder(productId, action, selectedSizeId){
    console.log('User is logged in, sending data.')

    /*var sizeSelect = document.getElementById('sizeSelect')*/
    var seletedSizeId;
    
    

    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({
            'productId': productId, 
            'action':action,
            'sizeId':selectedSizeId
        })
    })

    .then((response) => {
        return response.json();
    })
    .then((data) => {
        location.reload()
    });
    
}




function addCookieItem(productId, action){
    console.log('Not logged in')

    if(action == 'add'){
        if(cart[productId] == undefined){
            cart[productId] = {'quantity':1} 
        }else{
            cart[productId]['quantity'] += 1
        }

    }

    if(action == 'remove'){
        cart[productId]['quantity'] -= 1

        if(cart[productId]['quantity'] <= 0){
            console.log('Item should be deleted')
            delete cart[productId];
        }
    }
    console.log('CART: ', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()
}





