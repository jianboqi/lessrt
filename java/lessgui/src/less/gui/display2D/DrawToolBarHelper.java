package less.gui.display2D;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ThreadLocalRandom;

import org.omg.PortableInterceptor.SYSTEM_EXCEPTION;

import com.sun.prism.image.Coords;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Insets;
import javafx.scene.Cursor;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.control.Button;
import javafx.scene.control.Tooltip;
import javafx.scene.image.Image;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.ConstraintsBase;
import javafx.scene.paint.Color;
import javafx.scene.shape.Polygon;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import less.LessMainApp;
import less.gui.display3D.Display3DController;
import less.gui.helper.Filehelper;
import less.gui.helper.PyLauncher;
import less.gui.helper.RunningStatusThread;
import less.gui.model.OpticalThermalProperty;
import less.gui.model.PositionXY;
import less.gui.usercontrol.ImageButton;
import less.gui.utils.Const;
import less.gui.view.LessMainWindowController;
import za.co.luma.geom.Vector2DDouble;
import za.co.luma.math.sampling.Sampler;
import za.co.luma.math.sampling.UniformPoissonDiskSampler;

public class DrawToolBarHelper {
	
	private LessMainWindowController mwConstroller;
	//private double prex = -1;
	//private double prey = -1;
	ArrayList<Double> xs = new ArrayList<Double>();
	ArrayList<Double> ys = new ArrayList<Double>();
	public Canvas polygonLayer = null;
	public Canvas pointLayer = null;
	public Canvas backgroundLayer = null;
	private int addedPointNum = 0; // How many points have been added.
	private double zoomVal = 0.2; //zoomIn: 1.2 zoomOut 0.8
	private File backgroundImgFile = null;
	private double fisrt_x = 0;
	private double first_y = 0;
	
	public Display3DController display3dController;
	
	enum LayerType{
		POLYGON, POINT, BACKGROUND
	}
	
	enum ZoomMode{
		ZOOM_IN,ZOOM_OUT
	}
	
	
	public DrawToolBarHelper(LessMainWindowController mwConstroller){
		this.mwConstroller = mwConstroller;
	}
	
	public static void multiplyArray(double[] a, double b){
		for(int i=0;i<a.length;i++){
			a[i] = a[i]*b;
		}
	}
	
	public void initLayer(LayerType layerType){
		switch (layerType) {
		case POLYGON:
			if(polygonLayer == null){
				polygonLayer = new Canvas(mwConstroller.canvas.getWidth(),mwConstroller.canvas.getHeight());
				mwConstroller.AnchorInsideScrollPane.getChildren().add(polygonLayer);
				AnchorPane.setTopAnchor(polygonLayer, 0.0);
				AnchorPane.setLeftAnchor(polygonLayer, 0.0);
				polygonLayer.addEventFilter(MouseEvent.ANY, this.polygonListener);
			}
			polygonLayer.toFront();
			break;
		case POINT:
			if(pointLayer == null){
				pointLayer = new Canvas(mwConstroller.canvas.getWidth(),mwConstroller.canvas.getHeight());
				mwConstroller.AnchorInsideScrollPane.getChildren().add(pointLayer);
				AnchorPane.setTopAnchor(pointLayer, 0.0);
				AnchorPane.setLeftAnchor(pointLayer, 0.0);
				pointLayer.addEventFilter(MouseEvent.ANY, pointListener);
			}
			pointLayer.toFront();
			break;
		case BACKGROUND:
			if(backgroundLayer == null){
				backgroundLayer = new Canvas(mwConstroller.canvas.getWidth(),mwConstroller.canvas.getHeight());
				mwConstroller.AnchorInsideScrollPane.getChildren().add(backgroundLayer);
				AnchorPane.setTopAnchor(backgroundLayer, 0.0);
				AnchorPane.setLeftAnchor(backgroundLayer, 0.0);
			}
			backgroundLayer.toBack();
			break;

		default:
			break;
		}
	}
	
	public void resizeAllLayers(double newWidth, double newHeight){
		if(polygonLayer != null){
			polygonLayer.setWidth(newWidth);
			polygonLayer.setHeight(newHeight);
			
		}
		if(pointLayer != null){
			pointLayer.setWidth(newWidth);
			pointLayer.setHeight(newHeight);
		}
		
		if(backgroundLayer != null){
			backgroundLayer.setWidth(newWidth);
			backgroundLayer.setHeight(newHeight);
		}
	}
	
	
	/**
	 * ���ݴ�����polygon������л���
	 */
	public void reDrawPolygon(){
		if(polygonLayer != null && xs.size()>0 && mwConstroller.DrawPolygonCheckbox.isSelected()){
			 double width = mwConstroller.canvas.getWidth();
			 double height = mwConstroller.canvas.getHeight();
			 double w = Double.parseDouble(mwConstroller.sceneXSizeField.getText().replaceAll(",", ""));
			 double h = Double.parseDouble(mwConstroller.sceneYSizeField.getText().replaceAll(",", ""));
			 GraphicsContext gc = polygonLayer.getGraphicsContext2D();
			 gc.clearRect(0, 0, polygonLayer.getWidth(), polygonLayer.getHeight());
			 gc.setFill(Color.rgb(255, 0, 0,0.3));
			 double[] xspri = xs.stream().mapToDouble(d -> d).toArray();
			 multiplyArray(xspri, 1/w*width);
			 double[] yspri = ys.stream().mapToDouble(d -> d).toArray();
			 multiplyArray(yspri, 1/h*height);
			 gc.setStroke(Color.color(1, 0, 0));
			 gc.setLineWidth(2);
			 gc.strokePolygon(xspri,yspri, xs.size());
			 gc.fillPolygon(xspri,yspri, xs.size());
		}
	}
	
	/**
	 * ���Ʊ�����
	 */
	public void DrawBackground(){
		if(backgroundLayer != null && backgroundImgFile != null){
			GraphicsContext gc = backgroundLayer.getGraphicsContext2D();
        	Image image = new Image(this.backgroundImgFile.toURI().toString());
        	gc.drawImage(image, 0, 0, backgroundLayer.getWidth(), backgroundLayer.getHeight());
		}
	}
	
	/**
	 * ��ձ�����
	 */
	private void clearBackgroundImg(){
		if(this.backgroundLayer != null){
			this.backgroundImgFile = null;
			GraphicsContext gc = backgroundLayer.getGraphicsContext2D();
        	gc.clearRect(0, 0, this.backgroundLayer.getWidth(), this.backgroundLayer.getHeight());
		}
	}
	
	

	private EventHandler<MouseEvent> polygonListener = new EventHandler<MouseEvent>() {
	    @Override
	    public void handle(MouseEvent mouseEvent) {
	    	if(mwConstroller.DrawPolygonCheckbox.isSelected()){
	    		GraphicsContext gc = polygonLayer.getGraphicsContext2D();
	    		 double r=5;
	    		 if(mouseEvent.getEventType() == MouseEvent.MOUSE_CLICKED && mouseEvent.getButton() != MouseButton.SECONDARY){
	    			 double width = mwConstroller.canvas.getWidth();
	    			 double height = mwConstroller.canvas.getHeight();
	    			 double w = Double.parseDouble(mwConstroller.sceneXSizeField.getText().replaceAll(",", ""));
	    			 double h = Double.parseDouble(mwConstroller.sceneYSizeField.getText().replaceAll(",", ""));    			 	 
	    			 gc.clearRect(0, 0, polygonLayer.getWidth(), polygonLayer.getHeight());
	    			
	    			 double x = mouseEvent.getX();
	    			 double y = mouseEvent.getY();
	    			 double realx = x * w/width;
	    			 double realy = y * h/height;
	    			 xs.add(realx);
	    			 ys.add(realy);	
	    			 reDrawPolygon();
	    			 if(xs.size() == 1){
	    				 gc.setFill(Color.color(1, 0, 0));
		    			 gc.fillOval(x-r*0.5, y-r*0.5, r, r);
		    			 fisrt_x = x;
		    			 first_y = y;
	    			 }
	    			 //������֮����Ҫ��toolbar���ڶ��㣬��ֹ��canvas��Χ����toolbarʱ��toolbar������
	    			 mwConstroller.DrawToolBar.toFront();
	    			 //mwConstroller.canvasScrollPane.toFront();
			    }
	    		 if(mouseEvent.getEventType() == MouseEvent.MOUSE_CLICKED && mouseEvent.getButton() == MouseButton.SECONDARY){    			 
	    			 
	    			 if(xs.size() > 0){
	    				 xs.remove(xs.size()-1);
	    				 ys.remove(ys.size()-1);
	    				 reDrawPolygon();
	    			 }
	    			 if(xs.size() ==1){
	    				 gc.setFill(Color.color(1, 0, 0));
		    			 gc.fillOval(fisrt_x-r*0.5, first_y-r*0.5, r, r);
	    			 }
	    			 if(xs.size() ==0){
	    				 gc.clearRect(0, 0, polygonLayer.getWidth(), polygonLayer.getHeight());
	    			 }
	    			 
//	    			 xs.clear();
//	    			 ys.clear();
//	    			 gc.clearRect(0, 0, polygonLayer.getWidth(), polygonLayer.getHeight());
	    			 //prex = -1;
	    			 //prey = -1;
	    			 //gc.strokeLine(x, y, polygonList.get(0).x, polygonList.get(0).y);
	    		 }
	    		 
	    	}
	       
	    }
	};
	
	private EventHandler<MouseEvent> pointListener = new EventHandler<MouseEvent>() {
	    @Override
	    public void handle(MouseEvent mouseEvent) {
	    	if(mwConstroller.DrawPointCheckbox.isSelected()){
	    		GraphicsContext gc = pointLayer.getGraphicsContext2D();
	    		 if(mouseEvent.getEventType() == MouseEvent.MOUSE_CLICKED && mouseEvent.getButton() != MouseButton.SECONDARY){
	    			 double width = mwConstroller.canvas.getWidth();
	    			 double height = mwConstroller.canvas.getHeight();
	    			 double w = Double.parseDouble(mwConstroller.sceneXSizeField.getText().replaceAll(",", ""));
	    			 double h = Double.parseDouble(mwConstroller.sceneYSizeField.getText().replaceAll(",", ""));
	    				    			 
	    			 gc.clearRect(0, 0, pointLayer.getWidth(), pointLayer.getHeight());
	    			 double x = mouseEvent.getX();
	    			 double y = mouseEvent.getY();
	    			 double realx = x * w/width;
	    			 double realy = y * h/height;
	    			 if(mwConstroller.objectLV.getSelectionModel().getSelectedIndex() < 0){
							mwConstroller.outputConsole.log("Please choose an object.\n");
						}else{
							String objName = mwConstroller.objectLV.getSelectionModel().getSelectedItem();
							mwConstroller.objectAndPositionMap.get(objName).add(new PositionXY(realx +"", realy+""));
							addedPointNum++;
						}
	    			 mwConstroller.DrawToolBar.toFront();
	    			 
			    }
	    		 if(mouseEvent.getEventType() == MouseEvent.MOUSE_CLICKED && mouseEvent.getButton() == MouseButton.SECONDARY){
	    			 if(addedPointNum > 0){
	    				 String objName = mwConstroller.objectLV.getSelectionModel().getSelectedItem();
		    			 mwConstroller.objectAndPositionMap.get(objName).remove(mwConstroller.objectAndPositionMap.get(objName).size()-1);
		    			 addedPointNum--;
	    			 }
	    			 
	    		 }
	    		 
	    	}
	       
	    }
	};
	
	
	public void ZoomInAndOut(ZoomMode zoomMode){
		double zoomLevel = 1;
		if(zoomMode == ZoomMode.ZOOM_IN)
			zoomLevel += zoomVal;
		else {
			zoomLevel -= zoomVal;
		}
		double newwidth = zoomLevel*this.mwConstroller.canvas.getWidth();
		double newheight = zoomLevel*this.mwConstroller.canvas.getHeight();
		this.mwConstroller.drawHeper.max_canvas_length = Math.max(newwidth, newheight);
		this.mwConstroller.reDrawAll();
		
	}
	
	/**
	 * ����ά��ͼ����
	 */
	public void open3dViewer(Boolean isSimplified){
				
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(Display3DController.class.getResource("Display3DView.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			display3dController = loader.getController();
			display3dController.setParentController(this.mwConstroller);
			Scene scene = new Scene(rootLayout);
			Stage display3dStage = new Stage();
			display3dStage.setScene(scene);
			display3dStage.setTitle("3D viewer");
			display3dController.setParentStage(display3dStage);
			display3dController.setSimplified(isSimplified);
			display3dController.initDisplay3D();
			display3dStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			display3dStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			display3dStage.show();
			
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	
	/**
	 * ��ʼ������
	 */
	public void initDrawToolBar(){
		//scroll bar
		this.mwConstroller.canvasScrollPane.setFitToWidth(true);
		this.mwConstroller.canvasScrollPane.setFitToHeight(true);
		this.mwConstroller.canvasScrollPane.setMaxSize(Double.MAX_VALUE, Double.MAX_VALUE);
		
		//mask button
		ImageButton imageButton = new ImageButton(new Image(DrawToolBarHelper.class.getResourceAsStream("mask_filter.png")));
		imageButton.setPadding(Insets.EMPTY);
		Tooltip maskToolTip = new Tooltip();
		maskToolTip.setText("Applying a mask image to remove some of the objects.");
		imageButton.setTooltip(maskToolTip);
		this.mwConstroller.DrawToolBar.getItems().add(0, imageButton);
		imageButton.setOnAction(new EventHandler<ActionEvent>() {
		    @Override 
		    public void handle(ActionEvent e) {
		    	chooseMaskImg();
		    }
		});
		//background Image
		ImageButton backgroundImgBtn = new ImageButton(new Image(DrawToolBarHelper.class.getResourceAsStream("backgroundImg.png")));
		backgroundImgBtn.setPadding(Insets.EMPTY);
		Tooltip backgroundToolTip = new Tooltip();
		backgroundToolTip.setText("Add a background image.");
		backgroundImgBtn.setTooltip(backgroundToolTip);
		this.mwConstroller.DrawToolBar.getItems().add(1, backgroundImgBtn);
		backgroundImgBtn.setOnAction(new EventHandler<ActionEvent>() {
		    @Override 
		    public void handle(ActionEvent e) {
		    	initLayer(LayerType.BACKGROUND);
		    	chooseBackgroundImg();
		    }
		});
		
		//clear background Image
		ImageButton backgroundImgClearBtn = new ImageButton(new Image(DrawToolBarHelper.class.getResourceAsStream("backgroundImgClear.png")));
		backgroundImgClearBtn.setPadding(Insets.EMPTY);
		Tooltip backgroundImgClearToolTip = new Tooltip();
		backgroundImgClearToolTip.setText("Clear background image.");
		backgroundImgClearBtn.setTooltip(backgroundImgClearToolTip);
		this.mwConstroller.DrawToolBar.getItems().add(2, backgroundImgClearBtn);
		backgroundImgClearBtn.setOnAction(new EventHandler<ActionEvent>() {
		    @Override 
		    public void handle(ActionEvent e) {
		    	clearBackgroundImg();
		    }
		});
		
		//zoom button
		ImageButton zoomInButton = new ImageButton(new Image(DrawToolBarHelper.class.getResourceAsStream("Zoom-In-64.png")));
		zoomInButton.setPadding(Insets.EMPTY);
		Tooltip zoominToolTip = new Tooltip();
		zoominToolTip.setText("Zoom In.");
		zoomInButton.setTooltip(zoominToolTip);
		this.mwConstroller.DrawToolBar.getItems().add(3, zoomInButton);
		zoomInButton.setOnAction(new EventHandler<ActionEvent>() {
		    @Override 
		    public void handle(ActionEvent e) {
		    	ZoomInAndOut(ZoomMode.ZOOM_IN);
		    }
		});
		
		ImageButton zoomOutButton = new ImageButton(new Image(DrawToolBarHelper.class.getResourceAsStream("Zoom-Out-64.png")));
		zoomOutButton.setPadding(Insets.EMPTY);
		Tooltip zoomOutToolTip = new Tooltip();
		zoomOutToolTip.setText("Zoom Out.");
		zoomOutButton.setTooltip(zoomOutToolTip);
		this.mwConstroller.DrawToolBar.getItems().add(4, zoomOutButton);
		zoomOutButton.setOnAction(new EventHandler<ActionEvent>() {
		    @Override 
		    public void handle(ActionEvent e) {
		    	ZoomInAndOut(ZoomMode.ZOOM_OUT);
		    }
		});
		
		
		//3D view button
		ImageButton view3dbtn = new ImageButton(new Image(DrawToolBarHelper.class.getResourceAsStream("3dview.png")));
		view3dbtn.setPadding(Insets.EMPTY);
		Tooltip view3dbtnToolTip = new Tooltip();
		view3dbtnToolTip.setText("3D view.");
		view3dbtn.setTooltip(view3dbtnToolTip);
		this.mwConstroller.DrawToolBar.getItems().add(5, view3dbtn);
		view3dbtn.setOnAction(new EventHandler<ActionEvent>() {
		    @Override 
		    public void handle(ActionEvent e) {
		    	open3dViewer(false);
		    }
		});
		
		
		//minDistBtn
		Tooltip tooltip = new Tooltip();
		tooltip.setText("Minimum distance for poisson distribution.");
		mwConstroller.ImgBarMinDistTextField.setTooltip(tooltip);
		
		//add btn
		Tooltip tooltipAdd = new Tooltip();
		tooltipAdd.setText("Add trees with poisson distribution.");
		mwConstroller.AddTreePolyBtn.setTooltip(tooltipAdd);
		
		Tooltip tooltipApply = new Tooltip();
		tooltipApply.setText("Apply the selected objects to the points in the polygon.");
		mwConstroller.ApplyTreeSpeciesBtn.setTooltip(tooltipApply);
		
		
		///////////////////////////////////////////
		//////////////////////////////////////////
		//python console button
		ImageButton PyConsoleBtn = new ImageButton(new Image(DrawToolBarHelper.class.getResourceAsStream("pycode.png")));
		PyConsoleBtn.setPadding(Insets.EMPTY);
		Tooltip PyConsoleBtnToolTip = new Tooltip();
		PyConsoleBtnToolTip.setText("Python Console.");
		PyConsoleBtn.setTooltip(PyConsoleBtnToolTip);
		this.mwConstroller.ConsoleBarAnchorPane.getChildren().add(PyConsoleBtn);
		AnchorPane.setTopAnchor(PyConsoleBtn, 0.0);
		AnchorPane.setLeftAnchor(PyConsoleBtn, 5.0);
		PyConsoleBtn.setOnAction(new EventHandler<ActionEvent>() {
		    @Override 
		    public void handle(ActionEvent e) {
		    	mwConstroller.projManager.RunPythonConsole();
		    }
		});
//		
		/////////////////////////////////////////
		//////////////////////////////////////////
		
		
		this.mwConstroller.DrawPolygonCheckbox.selectedProperty().addListener(new ChangeListener<Boolean>() {
	        public void changed(ObservableValue<? extends Boolean> ov,
	            Boolean old_val, Boolean new_val) {
	                if(new_val){
	                	initLayer(LayerType.POLYGON);
	                	polygonLayer.setCursor(Cursor.HAND);
	                	mwConstroller.DelTreePolyBtn.setDisable(false);
	                	mwConstroller.AddTreePolyBtn.setDisable(false);
	                	mwConstroller.ApplyTreeSpeciesBtn.setDisable(false);
	                	mwConstroller.ImgBarMinDistTextField.setDisable(false);
	                	mwConstroller.DrawPointCheckbox.setSelected(false);
	                }
	                else{
	                	polygonLayer.setCursor(Cursor.DEFAULT);
	                	mwConstroller.DelTreePolyBtn.setDisable(true);
	                	mwConstroller.AddTreePolyBtn.setDisable(true);
	                	mwConstroller.ApplyTreeSpeciesBtn.setDisable(true);
	                	mwConstroller.ImgBarMinDistTextField.setDisable(true);
	                	GraphicsContext gc = polygonLayer.getGraphicsContext2D();
	                	gc.clearRect(0, 0, polygonLayer.getWidth(), polygonLayer.getHeight());
	                	xs.clear();
		    			ys.clear();
	                	
	                }
	                	
	        }
	    });
				
		
		//Del and Add button
		mwConstroller.DelTreePolyBtn.setOnAction((event) -> {
			if(xs.size()== 0){
				mwConstroller.outputConsole.log("Please draw a polygon.\n");
				return;
			}
			if(mwConstroller.simulation_path == null){
				mwConstroller.outputConsole.log("No simulation.\n");
				return;
			}
				
			double width = this.mwConstroller.canvas.getWidth();
			double height = this.mwConstroller.canvas.getHeight();
			String sceneX = this.mwConstroller.sceneXSizeField.getText();
			String sceneY = this.mwConstroller.sceneYSizeField.getText();
			double w = Double.parseDouble(sceneX.replaceAll(",", ""));
			double h = Double.parseDouble(sceneY.replaceAll(",", ""));
			
			
		   Polygon polygon = new Polygon();
		   Double[] coords = new Double[xs.size()*2];
		   for(int i=0;i<xs.size(); i++){
			   coords[i*2] = xs.get(i);
			   coords[i*2+1] = ys.get(i);
		   }
		   
		   polygon.getPoints().addAll(coords);
		   mwConstroller.StopDrawTree = true;
		   for(Map.Entry<String, ObservableList<PositionXY>> entry: mwConstroller.objectAndPositionMap.entrySet()){
				ObservableList<PositionXY> positionXYs = entry.getValue();
				Iterator<PositionXY> posIter = positionXYs.iterator();
				while(posIter.hasNext()){
					PositionXY posxy = posIter.next();
					double posx = Double.parseDouble(posxy.getPos_x());
					double posy = Double.parseDouble(posxy.getPos_y());
					//double tx = posx/w*width;
					//double ty = posy/h*height;
					if(polygon.contains(posx, posy)){
						posIter.remove();
					}
				}
				
			}     
		   mwConstroller.StopDrawTree = false;
		   mwConstroller.reDrawAll();
		});
		
		//Add button
		//Add
		mwConstroller.AddTreePolyBtn.setOnAction((event) -> {
			if(xs.size()== 0){
				mwConstroller.outputConsole.log("Please draw a polygon.\n");
				return;
			}
			if(mwConstroller.simulation_path == null){
				mwConstroller.outputConsole.log("No simulation.\n");
				return;
			}
			if(mwConstroller.objectsList.size() == 0){
				mwConstroller.outputConsole.log("No object defined.\n");
				return;
			}
			
			//ֻ������Щ��ѡ�е�
			ObservableList<String> selectedObjs = this.mwConstroller.objectLV.getSelectionModel().getSelectedItems();
			if(selectedObjs.size() == 0){//��ֻѡ�񲿷�ʱ����ֻ�Բ��ֽ�������
				System.out.println("Please choose at least one object to populate.");
				return;
			}
			int objNum = selectedObjs.size();
			
			double width = this.mwConstroller.canvas.getWidth();
			double height = this.mwConstroller.canvas.getHeight();
			String sceneX = this.mwConstroller.sceneXSizeField.getText();
			String sceneY = this.mwConstroller.sceneYSizeField.getText();
			double w = Double.parseDouble(sceneX.replaceAll(",", ""));
			double h = Double.parseDouble(sceneY.replaceAll(",", ""));
			
		   Polygon polygon = new Polygon();
		   Double[] coords = new Double[xs.size()*2];
		   for(int i=0;i<xs.size(); i++){
			   coords[i*2] = xs.get(i);
			   coords[i*2+1] = ys.get(i);
		   }
		   polygon.getPoints().addAll(coords);
		   
		   double minDist = Double.parseDouble(mwConstroller.ImgBarMinDistTextField.getText().replaceAll(",", ""));
		   
			Sampler<Vector2DDouble> sampler = new UniformPoissonDiskSampler(Collections.min(xs), 
					Collections.min(ys), Collections.max(xs), Collections.max(ys), minDist);
			List<Vector2DDouble> pointList = sampler.sample();
			String objName = mwConstroller.objectLV.getSelectionModel().getSelectedItem();
			mwConstroller.StopDrawTree = true;
			for(int i=0;i<pointList.size();i++){
				Vector2DDouble vec = pointList.get(i);
				//double tx = vec.x/w*width;
				//double ty = vec.y/h*height;
				if(polygon.contains(vec.x,vec.y)){
					int randomNum = ThreadLocalRandom.current().nextInt(0, objNum);
					mwConstroller.objectAndPositionMap.get(selectedObjs.get(randomNum)).add(new PositionXY(vec.x +"", vec.y+""));
				}
			}
			mwConstroller.StopDrawTree = false;
			mwConstroller.reDrawAll();
						
		});
		
		//��ѡ�е�objectӦ�õ����еĵ�֮��
		mwConstroller.ApplyTreeSpeciesBtn.setOnAction((event) -> {
			if(xs.size()== 0){
				mwConstroller.outputConsole.log("Please draw a polygon.\n");
				return;
			}
			if(mwConstroller.simulation_path == null){
				mwConstroller.outputConsole.log("No simulation.\n");
				return;
			}
			//ֻ������Щ��ѡ�е�
			ObservableList<String> selectedObjs = this.mwConstroller.objectLV.getSelectionModel().getSelectedItems();
			if(selectedObjs.size() == 0){//��ֻѡ�񲿷�ʱ����ֻ�Բ��ֽ�������
				System.out.println("Please choose at least one object to populate.");
				return;
			}
			int objNum = selectedObjs.size();
				
			double width = this.mwConstroller.canvas.getWidth();
			double height = this.mwConstroller.canvas.getHeight();
			String sceneX = this.mwConstroller.sceneXSizeField.getText();
			String sceneY = this.mwConstroller.sceneYSizeField.getText();
			double w = Double.parseDouble(sceneX.replaceAll(",", ""));
			double h = Double.parseDouble(sceneY.replaceAll(",", ""));
			
			
		   Polygon polygon = new Polygon();
		   Double[] coords = new Double[xs.size()*2];
		   for(int i=0;i<xs.size(); i++){
			   coords[i*2] = xs.get(i);
			   coords[i*2+1] = ys.get(i);
		   }
		   
		   polygon.getPoints().addAll(coords);
		   mwConstroller.StopDrawTree = true;
		   for(Map.Entry<String, ObservableList<PositionXY>> entry: mwConstroller.objectAndPositionMap.entrySet()){
			   String objName = entry.getKey();
			   ObservableList<PositionXY> positionXYs = entry.getValue();
				Iterator<PositionXY> posIter = positionXYs.iterator();
				while(posIter.hasNext()){
					PositionXY posxy = posIter.next();
					double posx = Double.parseDouble(posxy.getPos_x());
					double posy = Double.parseDouble(posxy.getPos_y());
					//double tx = posx/w*width;
					//double ty = posy/h*height;
					if(polygon.contains(posx, posy)){
						int randomNum = ThreadLocalRandom.current().nextInt(0, objNum);
						String randomName = selectedObjs.get(randomNum);
						if (!objName.equals(randomName)){
							mwConstroller.objectAndPositionMap.get(randomName).add(posxy);
							posIter.remove();
						}
						
					}
				}
				
			}     
		   mwConstroller.StopDrawTree = false;
		   mwConstroller.reDrawAll();
						
		});
		
		
		/////////////////////////////////////////////////////
		//for point draw
		////////////////////////////////////////////////////
		this.mwConstroller.DrawPointCheckbox.selectedProperty().addListener(new ChangeListener<Boolean>() {
	        public void changed(ObservableValue<? extends Boolean> ov,
	            Boolean old_val, Boolean new_val) {
	                if(new_val){
	                	initLayer(LayerType.POINT);
	                	pointLayer.setCursor(Cursor.HAND);
	                	mwConstroller.DrawPolygonCheckbox.setSelected(false);
	                }
	        }
	    });
		
		
		
	}
	
	/**
	 * ѡ��һ��mask�ļ�
	 */
	public void chooseMaskImg(){
		if(this.mwConstroller.simulation_path == null){
			this.mwConstroller.outputConsole.log("Please create a simulation first.\n");
			   return;
		}
		
		FileChooser fileChooser = new FileChooser();
		Path initPath = Paths.get(this.mwConstroller.simulation_path);
		File initDirectory = new File(initPath.normalize().toString());
		fileChooser.setInitialDirectory(initDirectory);
        // Set extension filter
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Geotiff", "*.tif"));
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ENVI Standard", "*.*"));
        // Show open file dialog
        File file = fileChooser.showOpenDialog(this.mwConstroller.mainApp.getPrimaryStage());
        if(file !=null)
        {
        	//����pythonǰ���ȱ���instances�ļ�
        	this.mwConstroller.save_tree_pos_xy();
        	//using python gdal to read and write 
        	String pyExe = PyLauncher.getPyexe();
        	String pyscripts = PyLauncher.getScriptsPath(Const.LESS_SCRIPTS_MASK);        	
        	ProcessBuilder pd=new ProcessBuilder(pyExe,pyscripts);
        	pd.directory(new File(this.mwConstroller.simulation_path));
//    		try {
////    			pd.redirectErrorStream(true);
//    			Process p = pd.start();
//    			BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
//    			String line;
//    			while ((line = input.readLine()) != null) {
//    				this.mwConstroller.outputConsole.appendText(line+"\n");
//    			}
//    			input = new BufferedReader(new InputStreamReader(p.getErrorStream()));
//    			while ((line = input.readLine()) != null) {
//    				this.mwConstroller.outputConsole.setErrorMode();
//    				this.mwConstroller.outputConsole.log(line+"\n");
//    			}
//    			p.waitFor();
//    		} catch (IOException | InterruptedException e) {
//    			e.printStackTrace();
//    		}
    		//update view
    		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwConstroller.objectAndPositionMap.entrySet()){
				entry.getValue().clear();
			}
    		this.mwConstroller.load_instances_file();
    		this.mwConstroller.reDrawAll();
    		
    		
    		
        }
        
	}
	
	/**
	 * ѡ��һ�������ļ�
	 */
	public void chooseBackgroundImg(){
		if(this.mwConstroller.simulation_path == null){
			this.mwConstroller.outputConsole.log("Please create a simulation first.\n");
			   return;
		}
		
		FileChooser fileChooser = new FileChooser();
		String lastOpened = this.mwConstroller.getLastOpenedPath(Const.LAST_OPNED_CHOOSE_BACKIMG);
		if (lastOpened != null && new File(lastOpened).exists()){
			fileChooser.setInitialDirectory(new File(lastOpened));
		}
        // Set extension filter
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Background Image", "*.jpg","*.png"));
        // Show open file dialog
        File file = fileChooser.showOpenDialog(this.mwConstroller.mainApp.getPrimaryStage());
        if(file !=null)
        {	
        	this.mwConstroller.setLastOpenedPath(Const.LAST_OPNED_CHOOSE_BACKIMG,file.getParent().toString());
        	this.backgroundImgFile = file;
        	DrawBackground();
        }
        
	}
	
	/**
	 * ��ȡpolygon
	 */
	public void onLoadPolygon(){
		if(!mwConstroller.DrawPolygonCheckbox.isSelected()){
			System.out.println("Polygon mode is not actived.");
			return;
		}
		
		FileChooser fileChooser = new FileChooser();
		String lastOpened = this.mwConstroller.getLastOpenedPath(Const.LAST_OPNED_CHOOSE_POLYGON);
		if (lastOpened != null && new File(lastOpened).exists()){
			fileChooser.setInitialDirectory(new File(lastOpened));
		}
        // Set extension filter
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Polygon", "*.txt"));
        // Show open file dialog
        File file = fileChooser.showOpenDialog(this.mwConstroller.mainApp.getPrimaryStage());
        if(file !=null)
        {	xs.clear();
        	ys.clear();
        	this.mwConstroller.setLastOpenedPath(Const.LAST_OPNED_CHOOSE_POLYGON,file.getParent().toString());
        	try (BufferedReader reader = new BufferedReader(new FileReader(file.toString()))) {
		        String line;
		        int objnum = 0;
		        while ((line = reader.readLine()) != null){
		        	if (!line.equals("")){
		        		String [] arr = line.trim().split(" ");
		        		double x = Double.parseDouble(arr[0]);
		        		double y = Double.parseDouble(arr[1]);
		        		xs.add(x);
		        		ys.add(y);
		        	}		        	
		        }  
		        reDrawPolygon();

		    } catch (IOException e) {
		    }
        }
	}
	
	/**
	 * ����polygon
	 */
	public void onSavePolygon(){
		
		if(xs.size() == 0){
			System.out.println("No pooygon to store.");
			return;
		}
		
		FileChooser fileChooser = new FileChooser();
		String lastOpened = this.mwConstroller.getLastOpenedPath(Const.LAST_OPNED_CHOOSE_POLYGON);
		if (lastOpened != null && new File(lastOpened).exists()){
			fileChooser.setInitialDirectory(new File(lastOpened));
		}
        // Set extension filter
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Polygon file", "*.txt"));
        // Show open file dialog
        File file = fileChooser.showSaveDialog(this.mwConstroller.mainApp.getPrimaryStage());
        if(file !=null)
        {	
        	this.mwConstroller.setLastOpenedPath(Const.LAST_OPNED_CHOOSE_POLYGON,file.getParent().toString());
        	String totalstr = "";
        	for(int i=0;i<xs.size();i++){
        		totalstr += xs.get(i) + " " + ys.get(i)+ "\n";
        	}
        	Filehelper.save_string_to_file(file.toString(), totalstr);
        }
	}
	
	
}
