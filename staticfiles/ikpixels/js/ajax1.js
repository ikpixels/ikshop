$(document).ready(function(){

    $('#QuoteForm').on('submit', function(event){
    event.preventDefault();
    var this_form = $(this);
    var url = this_form.attr('action');
    var data = this_form.serialize();

    $.ajax({
        type  : "POST",
        url   : url,
        data  : data,
        

        success : function(response){
           $('.contact-form-right').css('display','none');
           $('.contact-success').css('display','block');    
            
        },
        error :function(error){
            alert("error");
        }
    })
    
    
  });

   $('.newsletter-box').on('submit', function(event){
    event.preventDefault();
    var this_form = $(this);
    var url = this_form.attr('action');
    var data = this_form.serialize();

    $.ajax({
        type  : "POST",
        url   : url,
        data  : data,
        

        success : function(response){
           $('#Subscribe').css('display','block');
           //$('.contact-success').css('display','block');    
            
        },
        error :function(error){
            alert("error");
        }
    })
    
    
  });

})

