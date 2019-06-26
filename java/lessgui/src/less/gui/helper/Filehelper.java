package less.gui.helper;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

import javafx.collections.ObservableFloatArray;
import javafx.scene.shape.ObservableFaceArray;
import javafx.scene.shape.TriangleMesh;
import less.gui.model.LSBoundingbox;

public class Filehelper {
	public static void save_string_to_file(String filepath, String valueof){
		BufferedWriter writer = null;
		try
		{
		    writer = new BufferedWriter( new FileWriter(filepath));
		    writer.write(valueof);

		}
		catch ( IOException e)
		{
		}
		finally
		{
		    try
		    {
		        if ( writer != null)
		        writer.close( );
		    }
		    catch ( IOException e)
		    {
		    }
		}
	}
	
	
	
	
	/**
	 * save triangle mesh to obj file
	 * @param filepath
	 * @param triangleMesh
	 */
	public static void write_mesh_to_obj(String filepath, String groupName, TriangleMesh triangleMesh, 
			double fx, double fy, double fz,
			double offsetX, double offsetY, double offsetZ){
		BufferedWriter writer=null;
		try {
			writer = new BufferedWriter( new FileWriter(filepath));
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		 
		ObservableFloatArray pointarray =  triangleMesh.getPoints();
		ObservableFaceArray faces = triangleMesh.getFaces();
		
		try {
			writer.write("g "+groupName+"\n");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		for(int i=0;i<pointarray.size();i += 3){
			double x = pointarray.get(i)*fx-offsetX;
			double y = -pointarray.get(i+1)*fy-offsetY;
			double z = -pointarray.get(i+2)*fz-offsetZ;
			
			String out = "v ";
			out +=  Double.toString(x) + " " +
					Double.toString(y) + " " +
					Double.toString(z) + "\n";
			try {
				writer.write(out);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		for(int i=0;i<faces.size();i += triangleMesh.getFaceElementSize()){
			String out = "f ";
			out +=  Integer.toString(faces.get(i)+1) + " " +
					Integer.toString(faces.get(i+2)+1) + " " +
					Integer.toString(faces.get(i+4)+1) + "\n";
			try {
				writer.write(out);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		try {
			writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
}
