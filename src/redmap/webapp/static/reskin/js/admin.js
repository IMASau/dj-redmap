String.prototype.slugify = function() {
	var s = this;
	s = s.toLowerCase();
	s = s.replace(/\t+|\s+|\r+|\n+/g, '-');
	s = s.replace(/[^a-z0-9-]/g, '');
	return s;
}

$(function() {
	
	
	
	$('.lightbox-image').fancybox({
		type: 'image',
		autoScale: false,
		padding: 0,
		border: 0,
		width: 'auto',
		height: 'auto',
		autoScale: false,
		autoDimensions: false,
		titlePosition: 'inside',
		onComplete: function(currentArray, currentIndex, currentOpts){
			// remove previous
			$(".fancy-box-download-box").remove();
			
			$.each(currentArray, function(index, element){
				if( $(element).is('[data-image-url]') && $(element).is('[data-image-size]') )
				{
					var html = $("<div class=\"fancy-box-download-box\" style=\"padding: 10px\"><a target=\"_blank\" class=\"btn\" href=\"" + $(element).attr("data-image-url") + "\"><i class=\"icon-download-alt\"></i>  Download original image </a> Image filesize: " + $(element).attr("data-image-size") + "</div>");
					$("#fancybox-content").after(html);
				}
			});
		}
	});
});