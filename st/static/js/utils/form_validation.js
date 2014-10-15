/* 
input: array of 
 { element_id: options}
options :
{ minlength: x,
  required: true/false,
  email: true/false,
  equals: element_id,
}
*/
function validate(eles){
	errs = {} 
	for (element in eles ){
		options = eles[element];
		//1. required
		value = $('#'+element).val();
		value_exists = true;
		if ('required' in options && options['required'] == true){
			if (typeof value == 'undefined' || value.trim() == ''){
				msg = 'This field is required.';
				errs[element] = msg;
				value_exists = false;
			}
		}
		//2. email
		if ('email' in options && options['email'] == true){
			if (!validate_email(value)){
				msg = 'Please provide a valid email address';
				errs[element] = msg;
			}
		}
		//3. equals
		if ('equals' in options){
			target_id = options['equals'];
			target_val = $('#'+target_id).val();
			if (target_val != value){
				msg = 'It should be the same as '+$('#'+target_id).attr('name');
				errs[element] = msg;
			}		
		}
		//4. minlength
		if ('minlength' in options){
			if (value_exists && value.length < options['minlength']){
				msg = 'Length of '+$('#'+element).attr('name')+' should >='+options['minlength'];
				errs[element] = msg;
			}			
		} 
		//5 required checkbox for terms
		if ('checkbox' in options && 'terms' in options){
			if(! $('#'+element).prop("checked")){
				msg = "To participate, please indicate that you agree to the terms above";
				errs[element] = msg;
			}
		}

		//6 required radios for background
		if ('radio' in options){
			if(! $('[name="'+element+'"]').is(":checked")){
				msg = "please indicate your choice";
				errs[element] = msg;
			}else{
				errs[element]=false;
			}

		}
	}
	return errs;
}

function validate_email(value){
	return /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))$/i.test(value);

}


