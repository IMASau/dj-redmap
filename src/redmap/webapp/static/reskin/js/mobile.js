jQuery(function($) {
	
	if (!Modernizr.mq('only screen and (max-width: 767px)')) return false;

	var $nav 		= $('#nav'),
		$subnav		= $('#subnav');
		
	$nav.find('a').each(function() {	
	
		$(this).click(function(e) {
			e.stopImmediatePropagation();
			
			// if active region
			if ($(this).parent('li').hasClass('active')) {	
				$nav.toggleClass('expanded');
		
				if ($nav.hasClass('expanded') && $subnav.hasClass('expanded')) {
					$subnav.removeClass('expanded');
				}
				
				e.preventDefault();
				return false;
			}
			
		});
	});
	
	$subnav.click(function(e) {
		e.stopImmediatePropagation();
	
		$(this).toggleClass('expanded');
		
		if ($(this).hasClass('expanded') && $nav.hasClass('expanded')) {
			$nav.removeClass('expanded');
		}
	
		e.preventDefault();
		return false;
	});
	
	$(document).click(function(e) {
		$().add($subnav).add($nav).removeClass('expanded');
	});
	
	$subnav.find('a').click(function(e) {
		e.stopImmediatePropagation();
		e.preventPropagation();		
	});
	
});