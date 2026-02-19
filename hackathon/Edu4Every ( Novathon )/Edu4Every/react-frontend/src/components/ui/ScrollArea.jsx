import * as React from "react";
import * as ScrollAreaPrimitive from "@radix-ui/react-scroll-area";

const ScrollArea = React.forwardRef(({className, children, ...props}, ref) => (
  	<ScrollAreaPrimitive.Root ref={ref} className={className} {...props} >
		<ScrollAreaPrimitive.Viewport>{children}</ScrollAreaPrimitive.Viewport>	
		<ScrollBar />
		<ScrollAreaPrimitive.Corner />
	</ScrollAreaPrimitive.Root>	
));
ScrollArea.displayname= ScrollAreaPrimitive.Root.displayname;

const ScrollBar= React.forwardRef(({classNames}, ref)=>(
  	<ScrollAreaPrimitive.ScrollAreaScrollbar ref={ref} className={classNames} >
		<ScrollAreaPrimitive.ScrollAreaThumb />
	</ScrollAreaPrimitive.ScrollAreaScrollbar>	
));
ScrollBar.displayname= ScrollAreaPrimitive.ScrollAreaScrollbar.displayname;

export  {ScrollArea , ScrollBar};
