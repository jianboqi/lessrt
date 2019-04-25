package less.gui.helper;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.hamcrest.SelfDescribing;

import javafx.collections.ObservableFloatArray;
import javafx.collections.ObservableList;
import javafx.geometry.Point3D;
import javafx.scene.Node;
import javafx.scene.control.CheckBox;
import javafx.scene.shape.ObservableFaceArray;
import javafx.scene.shape.TriangleMesh;
import less.gui.display3D.DrawElement;
import less.gui.model.LSBoundingbox;
import less.gui.model.PositionXY;
import less.gui.utils.Const;
import less.gui.view.LAICalculatorController;

public class LAICaculatorThread extends Thread{
	private Thread t;
	private OutputConsole bdConsole;
	public LAICalculatorController laiController;
	
	public void prepare(LAICalculatorController laiController,OutputConsole bdConsole){
		this.laiController = laiController;
		this.bdConsole = bdConsole;
	}
	
	
	public void run(){
		synchronized (this) {
			LAICalculate();			
			notify();
		}
	}
	
	public void start () {
	      if (t == null) {
	         t = new Thread (this, "LAICalculator");
	         t.setUncaughtExceptionHandler((thread, throwable) -> {
	        	 bdConsole.setErrorMode();
	 			 bdConsole.log(throwable.getMessage());
	 			// notify to finish
	 			synchronized (this) {
	 				 notify();
	 			}
	         });
	         t.start ();
	      }
	   }
	
	public void stop_current_job(){
		
	}
	
	private ArrayList<String> getselectedComps(){
		ArrayList<String> selectedComps = new ArrayList<String>();
		for (Node checkbox : this.laiController.componentVBox.getChildren()) {
			if (checkbox instanceof CheckBox){
				CheckBox checkBox2 = (CheckBox)checkbox;
				if(checkBox2.isSelected())
					selectedComps.add((String)checkBox2.getUserData());
			}
		}
		return selectedComps;
	}
	
	class ObjectAreaAndMesh{
		double area=0;  //
		ArrayList<Point3D> points = new ArrayList<Point3D>(); //
		ArrayList<Integer> facets = new ArrayList<Integer>(); // 
	}
	
	private ObjectAreaAndMesh getObjectArea(ArrayList<TriangleMesh> meshList){
		
		ObjectAreaAndMesh objMesh = new ObjectAreaAndMesh();
		for(int k=0;k<meshList.size();k++){
			ObservableFloatArray pointarray =  meshList.get(k).getPoints();
			ObservableFaceArray faces = meshList.get(k).getFaces();
			int size = objMesh.points.size();
			for(int j=0;j<pointarray.size();j += 3){
				double x = pointarray.get(j);
				double y = -pointarray.get(j+1);
				double z = -pointarray.get(j+2);
				objMesh.points.add(new Point3D(x, y, z));
			}
			
			for(int i=0;i<faces.size();i += meshList.get(k).getFaceElementSize()){
				int index1 = faces.get(i)+size;
				int index2 = faces.get(i+2)+size;
				int index3 = faces.get(i+4)+size;
				objMesh.facets.add(index1);
				objMesh.facets.add(index2);
				objMesh.facets.add(index3);
				//
				Point3D p1 = objMesh.points.get(index1);
				Point3D p2 = objMesh.points.get(index2);
				Point3D p3 = objMesh.points.get(index3);
				Point3D p1_p2 = p2.subtract(p1);
				Point3D p1_p3 = p3.subtract(p1);
				Double triarea = p1_p2.crossProduct(p1_p3).magnitude()*0.5;
				objMesh.area += triarea;
			}
		}
		return objMesh;
	}
	
	
	private void parse_triangles(int wdith, int height,int depth, double colResolution, double rowResolution, double depthResolution,double objX,double objY,double objZ, ObjectAreaAndMesh objectAreaAndMesh, double [][][] lais){
		double factor = 1.0/3.0;
		for(int i=0;i<objectAreaAndMesh.facets.size();i+=3){
			Point3D p1 = objectAreaAndMesh.points.get(objectAreaAndMesh.facets.get(i));
			Point3D p2 = objectAreaAndMesh.points.get(objectAreaAndMesh.facets.get(i+1));
			Point3D p3 = objectAreaAndMesh.points.get(objectAreaAndMesh.facets.get(i+2));
			Point3D p1_p2 = p2.subtract(p1);
			Point3D p1_p3 = p3.subtract(p1);
			Double triarea = p1_p2.crossProduct(p1_p3).magnitude()*0.5;
			Point3D center = p1.add(p2).add(p3).multiply(factor);
			double x = objX - center.getX();
			double y = objY - center.getZ();
			double z = objZ + center.getY();
			int x_index = new Double(Math.floor(x/colResolution)).intValue();
			int y_index = new Double(Math.floor(y/rowResolution)).intValue();
			int z_index = new Double(Math.floor(z/depthResolution)).intValue();
			if (x_index>=0 && y_index >= 0 && z_index>=0 && x_index < wdith && y_index < height && z_index<depth)
				lais[y_index][x_index][z_index] += triarea;
		}
	}
	
   private void LAICalculate(){
 		if(this.laiController.mwController.simulation_path == null){
 			return;
 		}
 		this.bdConsole.log("INFO: LAI Calculation started.\n");
 		//double laiResolution = Double.parseDouble(this.laiController.LAITextField.getText().trim());
 		int laiRows = Integer.parseInt(this.laiController.textFieldRows.getText().trim());
 		int laiCols = Integer.parseInt(this.laiController.textFieldCols.getText().trim());
 		int laiHeight = Integer.parseInt(this.laiController.textFieldHeight.getText().trim());
 		
 		
 		
 		this.bdConsole.log("INFO: LAI Resolution: "+laiRows+" \u00D7 "+laiCols+" \u00D7 "+laiHeight+" \n");
 		double width = Double.parseDouble(this.laiController.mwController.sceneXSizeField.getText().replaceAll(",", ""));
 		double height = Double.parseDouble(this.laiController.mwController.sceneYSizeField.getText().replaceAll(",", ""));
 		//get Z height
 		double Depth = 0;
 		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.laiController.mwController.objectAndPositionMap.entrySet()){
 			String objName = entry.getKey();
 			ObservableList<PositionXY> positionXYZs = entry.getValue();
 			LSBoundingbox objBoundingbox = this.laiController.mwController.objectAndBoundingboxMap.get(objName);
 			for(int i=0;i<positionXYZs.size();i++){ //component
 				PositionXY posxyz = positionXYZs.get(i);
 				double z = Double.parseDouble(posxyz.getPos_z());
 				double tmp = z + objBoundingbox.getHeight();
 				if(tmp > Depth)
 					Depth = tmp;
 			}
 		}
 		
 		
// 		LSBoundingbox sceneBounds = new LSBoundingbox();
// 		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.laiController.mwController.objectAndPositionMap.entrySet()){
// 			String objName = entry.getKey();
// 			ObservableList<PositionXY> positionXYZs = entry.getValue();
// 			LSBoundingbox objBoundingbox = this.laiController.mwController.objectAndBoundingboxMap.get(objName);
// 			for(int i=0;i<positionXYZs.size();i++){ //component
// 				PositionXY posxyz = positionXYZs.get(i);
// 				double x = Double.parseDouble(posxyz.getPos_x());
// 				double y = Double.parseDouble(posxyz.getPos_y());
// 				double z = Double.parseDouble(posxyz.getPos_z());
// 				//x, y is not correct here, we only take the value of z
// 				sceneBounds = LSBoundingbox.merge(sceneBounds, objBoundingbox.getOffsetedBoundingbox(x, z, y));
// 			}
// 		}
// 		double Depth = sceneBounds.getHeight(); 
 		System.out.println("Scene Depth [m]: "+Depth);
 		
 		
 		double [][][] lais = new double [laiRows][laiCols][laiHeight];
 		double rowResolution = height/laiRows;
 		double colResolution = width/laiCols;
 		double depthResolution = Depth/laiHeight;
 		
 		
 		//Map<String, Double> opticalcomponentArea = new HashMap<String, Double>();		
 		ArrayList<String> selectedComps = this.getselectedComps();
 		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.laiController.mwController.objectAndPositionMap.entrySet()){
 			String objName = entry.getKey();
 			this.bdConsole.log("INFO: Processing object: "+objName+"\n");
 			LSBoundingbox objBoundingbox = this.laiController.mwController.objectAndBoundingboxMap.get(objName);
 			double xExtent = objBoundingbox.getXExtent();
 			double yExtent = objBoundingbox.getYExtent();
 			double zExtent = objBoundingbox.getHeight();
 			ObservableList<PositionXY> positionXYZs = entry.getValue();
 			
 			Map<String, ObjectAreaAndMesh> objectArea = new HashMap<String, ObjectAreaAndMesh>();
 			
 			ArrayList<TriangleMesh> objectMeshes = new ArrayList<TriangleMesh>();
 			ObservableList<String> comps = this.laiController.mwController.objectsAndCompomentsMap.get(objName);
 			for(int i=0;i<comps.size();i++){
 				String compName = comps.get(i);
 				if(selectedComps.contains(compName)){
 					String objPath = Paths.get(this.laiController.mwController.projManager.getParameterDirPath(),compName).toString();
 					TriangleMesh mesh = (TriangleMesh)DrawElement.getMeshFromObj(objPath)[0];
 					objectMeshes.add(mesh);
 				}
 			}
 			
 			for(int i=0;i<positionXYZs.size();i++){ //component
 				PositionXY posxyz = positionXYZs.get(i);
 				double x = Double.parseDouble(posxyz.getPos_x());
 				double y = Double.parseDouble(posxyz.getPos_y());
 				double z = Double.parseDouble(posxyz.getPos_z());
 				double left = x - 0.5*xExtent;
 				double right = x + 0.5*xExtent;
 				double up = y - 0.5*yExtent;
 				double down = y + 0.5*yExtent;
 				double bottom = z;
 				double above = z+zExtent;
 				
 				int left_index = new Double(Math.floor(left/colResolution)).intValue();
 				int right_index = new Double(Math.floor(right/colResolution)).intValue();
 				int up_index = new Double(Math.floor(up/rowResolution)).intValue();
 				int down_index = new Double(Math.floor(down/rowResolution)).intValue();
 				int bottom_index = new Double(Math.floor(bottom/depthResolution)).intValue();
 				int above_index = new Double(Math.floor(above/depthResolution)).intValue();
 				if(above == depthResolution) above_index = 0;
 				
 				//
 				if(left_index == right_index && up_index == down_index && bottom_index == above_index){
 					if(objectArea.containsKey(objName)){
 						lais[up_index][left_index][bottom_index] += objectArea.get(objName).area;
 					}else{
 						ObjectAreaAndMesh objectAreaAndMesh = this.getObjectArea(objectMeshes);
 						lais[up_index][left_index][bottom_index] += objectAreaAndMesh.area;
 						objectArea.put(objName, objectAreaAndMesh);
 					}
 				}else{//
 					if(!objectArea.containsKey(objName)){
 						objectArea.put(objName, this.getObjectArea(objectMeshes));
 					}
 					this.parse_triangles(laiCols,laiRows,laiHeight,colResolution,rowResolution,depthResolution, x, y,z, objectArea.get(objName), lais);
 				}
 			}
 		}
 		
 		String lai_output_file = Paths.get(this.laiController.mwController.projManager.getResultsDirPath(),Const.LESS_LAI_OUTPUT_FILE).toString();
		
		try {
			BufferedWriter writer = new BufferedWriter( new FileWriter(lai_output_file));
			writer.write("Scene Size [X, Y, Z]: "+String.format("%.4f ",width)+" "+String.format("%.4f ",height)+" "+String.format("%.4f ",Depth)+"\n");
			writer.write("LAI Dimension [Rows, Cols, height]: "+laiRows+" "+laiCols+" "+laiHeight+"\n");
			for(int k=0;k<laiHeight;k++) {
				for(int i = 0;i<laiRows;i++){
		 			for(int j=0;j<laiCols;j++){
						writer.write(String.format("%.4f ", lais[i][j][k]/colResolution/rowResolution));
		 			}
		 			writer.write("\n");
		 		}
				writer.write("\n");
			}
	 		
	 		
	 		writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		this.bdConsole.log("INFO: Writing results to "+Const.LESS_LAI_OUTPUT_FILE+"\n");
 		this.bdConsole.log("INFO: Done.\n");
	 		
   }
	
	
	
	
}
