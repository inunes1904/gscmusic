var updateButtons = document.getElementsByClassName('update-cart')

for (var i=0; i < updateButtons.length; i++){
    updateButtons[i].addEventListener('click', function(){
        // aqui trazemos o datasource que no nosso caso e o button data-product
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action', action)

        // aqui verificamos o utilizador esta ou nao autenticado
        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            addCookieItem(productId, action)
        }else{
            updateUserOrder(productId, action)
        }
    })
}


function addCookieItem(productId,action){
    console.log('User is not authenticated')
    if (action == 'add'){
        if (cart[productId] == undefined){
            cart[productId] = {'quantity':1}
        }else{
            cart[productId]['quantity'] +=1
        }
    }
    if (action == 'remove'){
        
            cart[productId]['quantity'] -=1
            if(cart[productId]['quantity'] <= 0){
                console.log('Item should be deleted')
                delete cart[productId]
            }
        }
        console.log('Cart:', cart)
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
        location.reload()
    }



function updateUserOrder(productId, action){
    console.log('User is authenticated, sending data')

    var url = '/update_item/'
    // para enviar as novas informaçoes para o carrinho vamos usar um fetch
    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        // como nao podemos enviar apenas os dados para o backend utilizamos o json Stringify
        body:JSON.stringify({'productId':productId, 'action':action})
    })
    // reposta do backend
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log('Data:', data)
        location.reload()
    })
}