function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


document.addEventListener("DOMContentLoaded", function () {

    const btns = document.querySelectorAll(".btn-addto-cart");


    btns.forEach(btn => {
        btn.addEventListener("click", addToCart);
    });
});


function addToCart(event) {

    let productId = event.target.dataset.productId;
    let url="/add-to-cart"
    let data={id:productId}

    fetch(url,{
       method:'POST',
       headers:{'Content-Type':'application/json','X-CSRFToken': csrftoken},
       body:JSON.stringify(data)
    })
    .then(res=>res.json())
    .then(data=>{
       console.log(data)
    })
    .catch(error=>{
       console.log(error)
    })
}
