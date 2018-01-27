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
		System.out.println(objMesh.area);
		return objMesh;
	}
	
	
	private void parse_triangles(int wdith, int height, double laiResolution,double objX,Double objY, ObjectAreaAndMesh objectAreaAndMesh, double [][] lais){
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
			int x_index = new Double(Math.floor(x/laiResolution)).intValue();
			int y_index = new Double(Math.floor(y/laiResolution)).intValue();
			if (x_index>0 && y_index > 0 && x_index < wdith && y_index < height)
				lais[y_index][x_index] += triarea;
		}
	}
	
   private void LAICalculate(){
	 		if(this.laiController.LAITextField.getText().equals("")){
	 			return;
	 		}
	 		if(this.laiController.mwController.simulation_path == null){
	 			return;
	 		}
	 		this.bdConsole.log("INFO: LAI Calculation started.\n");
	 		double laiResolution = Double.parseDouble(this.laiController.LAITextField.getText().trim());
	 		this.bdConsole.log("INFO: LAI Resolution: "+laiResolution+" \n");
	 		double width = Double.parseDouble(this.laiController.mwController.sceneXSizeField.getText().replaceAll(",", ""));
	 		double height = Double.parseDouble(this.laiController.mwController.sceneYSizeField.getText().replaceAll(",", ""));
	 		double dcols = Math.ceil(width/laiResolution);
	 		double drows = Math.ceil(height/laiResolution);
	 		int rows = (new Double(drows)).intValue();
	 		int cols = (new Double(dcols)).intValue();
	 		double [][] lais = new double [rows][cols];
	 		Map<String, Double> opticalcomponentArea = new HashMap<String, Double>();		
	 		ArrayList<String> selectedComps = this.getselectedComps();
	 		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.laiController.mwController.objectAndPositionMap.entrySet()){
	 			String objName = entry.getKey();
	 			this.bdConsole.log("INFO: Processing object: "+objName+"\n");
	 			LSBoundingbox objBoundingbox = this.laiController.mwController.objectAndBoundingboxMap.get(objName);
	 			double xExtent = objBoundingbox.getXExtent();
	 			double yExtent = objBoundingbox.getYExtent();
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
	 				double left = x - 0.5*xExtent;
	 				double right = x + 0.5*xExtent;
	 				double up = y - 0.5*yExtent;
	 				double down = y + 0.5*yExtent;
	 				
	 				int left_index = new Double(Math.floor(left/laiResolution)).intValue();
	 				int right_index = new Double(Math.floor(right/laiResolution)).intValue();
	 				int up_index = new Double(Math.floor(up/laiResolution)).intValue();
	 				int down_index = new Double(Math.floor(down/laiResolution)).intValue();
	 				//
	 				if(left_index == right_index && up_index == down_index){
	 					if(objectArea.containsKey(objName)){
	 						lais[up_index][left_index] += objectArea.get(objName).area;
	 					}else{
	 						ObjectAreaAndMesh objectAreaAndMesh = this.getObjectArea(objectMeshes);
	 						lais[up_index][left_index] += objectAreaAndMesh.area;
	 						objectArea.put(objName, objectAreaAndMesh);
	 					}
	 				}else{//
	 					if(!objectArea.containsKey(objName)){
	 						objectArea.put(objName, this.getObjectArea(objectMeshes));
	 					}
	 					this.parse_triangles(cols,rows,laiResolution, x, y, objectArea.get(objName), lais);
	 				}
	 			}
	 		}
	 		
	 		String lai_output_file = Paths.get(this.laiController.mwController.projManager.getResultsDirPath(),Const.LESS_LAI_OUTPUT_FILE).toString();
			
			try {
				BufferedWriter writer = new BufferedWriter( new FileWriter(lai_output_file));
				
		 		for(int i = 0;i<rows;i++){
		 			for(int j=0;j<cols;j++){
						writer.write(String.format("%.4f ", lais[i][j]/laiResolution/laiResolution));
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
