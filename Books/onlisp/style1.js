/* ---------- setting ------------------------------- */
cssfolder = "css/";
styleFiles = new Array("No_StyleSheet","meadow","midnight","white","gray","print");
first = 3; 



/* -------------------------------------------------- */
var IE4=false;
var IE5=false;
var NN4=false;
var NN6=false;
var OPE=false;

if(navigator.appName.search(/Opera/i)>=0){OPE = true}
else if(document.all && !document.getElementById){IE4 = true}
else if(document.all && document.getElementById){IE5 = true}
else if(!OPE && !document.all && document.getElementById){NN6 = true}
else if(document.layers){NN4 = true}




selectedStyleNumber = loadCookie("cssnum");

if(!loadCookie("cssnum")||Math.round(selectedStyleNumber)>styleFiles.length){
	selectedStyleNumber = first;
}
selectedStyleNumber = Math.round(selectedStyleNumber);

if(selectedStyleNumber>0){
	if(IE4 || IE5){
		document.styleSheets[0].href = cssfolder + styleFiles[selectedStyleNumber] + ".css";
	}else if(NN6){
		document.styleSheets[0].disabled=true;
		document.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"" + cssfolder + styleFiles[selectedStyleNumber] + ".css\">");
	}else if(OPE && document.getElementById('css1')){
		document.getElementById('css1').href = cssfolder + styleFiles[selectedStyleNumber] + ".css";
	}
}else{
	if(document.all || document.getElementById){
		for(i=0;i<document.styleSheets.length;i++){
			document.styleSheets[i].disabled=true;
		}
	}else if(OPE && document.getElementById('css1')){
		document.getElementById('css1').href=null;
	}
}


function loadCookie(arg){ //arg=dataname
	if(arg){
		cookieData = document.cookie + ";" ;
		arg = escape(arg);
		startPoint1 = cookieData.indexOf(arg);
		startPoint2 = cookieData.indexOf("=",startPoint1) +1;
		endPoint = cookieData.indexOf(";",startPoint1);
		if(startPoint2 < endPoint && startPoint1 > -1 &&startPoint2-startPoint1 == arg.length+1){
			cookieData = cookieData.substring(startPoint2,endPoint);
			cookieData = unescape(cookieData);
			return cookieData
		}
	}
	return false
}

/*-------------------------------------
(c) 2002 DFJ
http://www.fromdfj.net/
info@fromdfj.net
-------------------------------------*/
