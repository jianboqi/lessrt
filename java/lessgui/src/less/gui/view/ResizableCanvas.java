package less.gui.view;

import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;

public class ResizableCanvas extends Canvas{
	public ResizableCanvas() {
	      // Redraw canvas when size changes.
	      widthProperty().addListener(evt -> draw());
	      heightProperty().addListener(evt -> draw());
	    }
	
		private void drawBasicGrids(){
			double width = getWidth();
		    double height = getHeight();
		    double gridNum = 20.0;
		    double interval_x = width/gridNum;
		    double interval_y = height/gridNum;
		    GraphicsContext gc = getGraphicsContext2D();
		    gc.clearRect(0, 0, width, height);
		    gc.setStroke(Color.GREEN);
		    for(int i=0;i<gridNum;i++){
		    	double xpos = i * interval_x;
		    	gc.strokeLine(xpos, 0, xpos, height);
		    }
		    for(int j=0;j<gridNum;j++){
	    		double ypos = j * interval_y;
	    		gc.strokeLine(0, ypos, width, ypos);
	    	}
		 
		}
	 
	    private void draw() {
	    	drawBasicGrids();
	    }
	 
	    @Override
	    public boolean isResizable() {
	      return false;
	    }
	 
	    @Override
	    public double prefWidth(double height) {
	      return getWidth();
	    }
	 
	    @Override
	    public double prefHeight(double width) {
	      return getHeight();
	    }
}
