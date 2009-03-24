if(document.all||document.getElementById){
	formHtml = new Array;
	i=0;
	formHtml[i++]="<form \"javascript:void(0)\">";
	formHtml[i++]="<div><label for=\"stylebox\">CSS Change</label>";
	formHtml[i++]="<select id=\"styleBox\" onchange=\"changeStyle(this.form.elements[0].selectedIndex)\">";
	for(j=0;j<styleFiles.length;j++){
		if(j==selectedStyleNumber)formHtml[i++] = "<option selected=\"selected\">" + styleFiles[j] + "</option>";
		else formHtml[i++] = "<option>" + styleFiles[j] + "</option>";
	}
	formHtml[i++] = "</select></div></form>";

	document.write(formHtml.join("\n"));
}

function changeStyle(num){
	if(num!=0){
		saveCookie("cssnum",num+"",3);
		if(document.all){
			document.styleSheets[0].disabled=false;
		}
		location.replace(location.href);
	}
	else if(num==0){
		saveCookie("cssnum",num+"",3);
		if(document.all){
			for(i=0;i<document.styleSheets.length;i++){
				document.styleSheets[i].disabled=true;
			}
		}
		else if(!document.all)location.replace(location.href) ;
	}
}

function saveCookie(arg1,arg2,arg3){ //arg1=dataname arg2=data arg3=expiration days
	if(arg1&&arg2){
		if(arg3){
			xDay = new Date;
			xDay.setDate(xDay.getDate() + eval(arg3));
			xDay = xDay.toGMTString();
			_exp = ";expires=" + xDay;

			yDay = new Date;
			yDay.setDate(yDay.getDate() - 1);
			yDay = yDay.toGMTString();
			_yexp = ";expires=" + xDay;
			
		}
		
		else _exp ="";
		document.cookie = escape(arg1) + "=" + escape(arg2) + _exp;
	}
}


/*-------------------------------------
(c) 2002 DFJ
http://www.fromdfj.net/
info@fromdfj.net
-------------------------------------*/