package less.gui.helper;

import java.util.Map;

import javafx.collections.ObservableList;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;
import javafx.scene.transform.Affine;
import javafx.scene.transform.Transform;
import less.gui.display2D.DrawingUtils;
import less.gui.model.PositionXY;
import less.gui.utils.Const;
import less.gui.utils.RandomColorFactory;
import less.gui.view.LessMainWindowController;

public class DrawHelper {
	private LessMainWindowController mwController;
	public double max_canvas_length = 500;
	private RandomColorFactory RndColorFactory = new RandomColorFactory();

	public DrawHelper(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	/**
	 * Draw basic grids on the canvas
	 */
	public void drawBasicGrids(){
		double width = this.mwController.canvas.getWidth();
		double height = this.mwController.canvas.getHeight();
		double gridNum = 20.0;
	    double interval_x = width/gridNum;
	    double interval_y = height/gridNum;
	    GraphicsContext gc = this.mwController.canvas.getGraphicsContext2D();
	    gc.clearRect(0, 0, width, height);
	    gc.setStroke(Color.GRAY);
	    for(int i=0;i<gridNum+1;i++){
	    	double xpos = i * interval_x;
	    	gc.strokeLine(xpos, 0, xpos, height);
	    }
	    for(int j=0;j<gridNum+1;j++){
    		double ypos = j * interval_y;
    		gc.strokeLine(0, ypos, width, ypos);
    	}
	}
	
	public void drawSunAndView(){
		if (this.mwController.sunAzimuthField.getText().equals(""))
			return;
		double width = this.mwController.canvas.getWidth();
		double height = this.mwController.canvas.getHeight();
		double r = 20;
		double R = Math.min(width*0.5, height*0.5)-r*0.5;
		double sun_azimuth = Double.parseDouble(this.mwController.sunAzimuthField.getText().replaceAll(",", ""));
		double phi = -(sun_azimuth - 90) / 180.0 * Math.PI;
		double x = R*Math.cos(phi)+width*0.5;
		double y = height*0.5-R*Math.sin(phi);
		GraphicsContext gc = this.mwController.canvas.getGraphicsContext2D();
		gc.setFill(Color.color(0.9176, 0.5568, 0.0117));
		gc.fillOval(x-r*0.5, y-r*0.5, r, r);
		gc.setStroke(Color.color(0.9176, 0.5568, 0.0117));
		gc.setLineWidth(3);
		DrawingUtils.drawArrow(gc, x, y, x+0.5*(width*0.5-x), y+0.5*(height*0.5-y));
		gc.setLineWidth(1);
		
		//只有平行投影下才绘制观测方向
		if(this.mwController.comboBoxSensorType.getSelectionModel().getSelectedItem().equals(Const.LESS_SENSOR_TYPE_ORTH)){
			if(this.mwController.obsAzimuthField.getText().equals(""))
				return;
			double view_azimuth = Double.parseDouble(this.mwController.obsAzimuthField.getText().replaceAll(",", ""));
			phi = -(view_azimuth - 90) / 180.0 * Math.PI;
			x = R*Math.cos(phi)+width*0.5;
			y = height*0.5-R*Math.sin(phi);
			gc.setLineWidth(3);
			gc.setFill(Color.GREEN);
			gc.setStroke(Color.GREEN);
			gc.strokeOval(x-r, y-r*0.5, r*2, r);
			gc.fillOval(x-r*0.25, y-r*0.5, 0.5*r, r);
			DrawingUtils.drawArrow(gc, x, y, x+0.5*(width*0.5-x), y+0.5*(height*0.5-y));
			gc.setLineWidth(1);
		}
	}	
	
	/**
	 * Redraw basic grids when changing the terrain size
	 */
	public void reDrawAll(){
		String sceneX = this.mwController.sceneXSizeField.getText();
		String sceneY = this.mwController.sceneYSizeField.getText();
		if (!sceneX.equals("") && !sceneY.equals("")){
			double w = Double.parseDouble(sceneX.replaceAll(",", ""));
			double h = Double.parseDouble(sceneY.replaceAll(",", ""));
			if(w >= h){
				this.mwController.canvas.setWidth(max_canvas_length);
				this.mwController.canvas.setHeight(max_canvas_length*h/w);
				this.mwController.drawtoolBarHelper.resizeAllLayers(max_canvas_length, max_canvas_length*h/w);
			}
			else{
				this.mwController.canvas.setWidth(max_canvas_length*w/h);
				this.mwController.canvas.setHeight(max_canvas_length);
				this.mwController.drawtoolBarHelper.resizeAllLayers(max_canvas_length*w/h, max_canvas_length);
			}
			//当在polygon模式时，如果改变canvas大小，polygon和背景跟着变。
			this.mwController.drawtoolBarHelper.reDrawPolygon();
			this.mwController.drawtoolBarHelper.DrawBackground();
			this.drawBasicGrids();
		}
		//redraw forest
		drawTreePosition();
		drawSunAndView();
		drawOrthgraphicCameraAndSensor();
		
		//redraw 3D view
		//如果3D视图存在，则重绘
		if(this.mwController.drawtoolBarHelper.display3dController != null){
			this.mwController.drawtoolBarHelper.display3dController.drawLightRay();
			this.mwController.drawtoolBarHelper.display3dController.drawCamerafrustum();
		}
		
		
	}
	
	
	//forest
	
	public void drawTreePosition(){
		
		//根据选择，如果不现实，则不绘制
		if(!this.mwController.displayPosOn2DCheck.isSelected()){
			return;
		}
		
		//隐藏选中得objects
		ObservableList<String> tobeHide = null;
		if(this.mwController.HideSelectedCheck.isSelected()){
			tobeHide = this.mwController.objectLV.getSelectionModel().getSelectedItems();
		}
        
      //draw on the canvas
		RndColorFactory.Reset();
        double width = this.mwController.canvas.getWidth();
		double height = this.mwController.canvas.getHeight();
		String sceneX = this.mwController.sceneXSizeField.getText();
		String sceneY = this.mwController.sceneYSizeField.getText();
		double w = Double.parseDouble(sceneX.replaceAll(",", ""));
		double h = Double.parseDouble(sceneY.replaceAll(",", ""));
		GraphicsContext gc = this.mwController.canvas.getGraphicsContext2D();
		double r = 4;
		int totalNum = 0;
		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
			totalNum += entry.getValue().size();
		}  
        if(totalNum <= Const.LESS_TREE_POS_DRAW_MAX_NUM){
        	for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
    			String objName = entry.getKey();
    			if(tobeHide!=null && tobeHide.contains(objName)){
    				RndColorFactory.advance();
    				continue;
    			}
    			ObservableList<PositionXY> positionXYs = entry.getValue();
    			if(positionXYs.size() > 1000)
    				r = 1;
    			gc.setFill(RndColorFactory.getColor());
    			for(int i=0;i<positionXYs.size();i++){ //component
    				PositionXY posxy = positionXYs.get(i);
    				double tx = Double.parseDouble(posxy.getPos_x().replaceAll(",", ""));
    				double ty = Double.parseDouble(posxy.getPos_y().replaceAll(",", ""));
    				gc.fillOval(tx/w*width-r, ty/h*height-r, 2*r, 2*r);
    			}
    			
    		} 
        }else{
        	mwController.outputConsole.log("Object positions are not drawed, The maximum number of drawing is " + Const.LESS_TREE_POS_DRAW_MAX_NUM +".\n");
        }
	}
	
	
	
	/**
	 * Draw the range of sensor print according to the zenith, azimuth of sensor
	 */
	public void drawOrthgraphicCameraAndSensor(){
		if(this.mwController.comboBoxSensorType.getSelectionModel().getSelectedItem().equals(Const.LESS_SENSOR_TYPE_ORTH)){
			String xExtent = this.mwController.sensorXExtentField.getText();
			String yExtent = this.mwController.sensorYExtentField.getText();
			String sceneX = this.mwController.sceneXSizeField.getText();
			String sceneY = this.mwController.sceneYSizeField.getText();
			String viewAzimuth = this.mwController.obsAzimuthField.getText();
			String viewZenith = this.mwController.obsZenithField.getText();
			if(xExtent.equals("") || yExtent.equals("") || sceneX.equals("") || sceneY.equals("")||
					viewAzimuth.equals("") || viewZenith.equals("")){
				return;
			}
			double width = this.mwController.canvas.getWidth();
			double height = this.mwController.canvas.getHeight();
			double sensorXExtent = Double.parseDouble(xExtent.replaceAll(",", ""));
			double sensorYExtent = Double.parseDouble(yExtent.replaceAll(",", ""));
			double scenew = Double.parseDouble(sceneX.replaceAll(",", ""));
			double sceneh = Double.parseDouble(sceneY.replaceAll(",", ""));
			double viewZenithAngle = Double.parseDouble(viewZenith.replaceAll(",", ""))/180.0*Math.PI;
			double viewAzimuthAngle = Double.parseDouble(viewAzimuth.replaceAll(",", ""))/180.0*Math.PI;
			double scale_pixel_real = width/scenew; //pixels per meter
			GraphicsContext gc = this.mwController.canvas.getGraphicsContext2D();
			if(scenew<sensorXExtent || sceneh < sensorYExtent){
				this.mwController.mapInfoLabel.setText("Attention: Sensor ranges exceed the actual scene.");
			}else{
				this.mwController.mapInfoLabel.setText("");
			}
			//along front: height direction
			double sensor_height_projected_range = sensorYExtent/Math.cos(viewZenithAngle);
			
			double sensorPixelWidth = sensorXExtent*scale_pixel_real;
			double sensorPixelHeight = sensor_height_projected_range*scale_pixel_real;
			double x = 0.5*width - 0.5*sensorPixelWidth;
			double y = 0.5*height - 0.5*sensorPixelHeight;
			
			Transform transform = Transform.rotate(Math.toDegrees(-Math.PI + viewAzimuthAngle), 0.5*width, 0.5*height);
			gc.setTransform(new Affine(transform));
			gc.setStroke(Color.BLUE);
			gc.setLineWidth(3);
			gc.strokeRect(x, y, sensorPixelWidth, sensorPixelHeight);
			gc.setLineWidth(1);
			gc.setTransform(new Affine());
		}
	}
	
	
}
