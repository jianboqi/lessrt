package less.gui.display3D;

import java.awt.List;
import java.nio.file.Paths;
import java.util.ArrayList;

import org.apache.commons.io.filefilter.AndFileFilter;

import com.interactivemesh.jfx.importer.ImportException;
import com.interactivemesh.jfx.importer.obj.ObjModelImporter;

import javafx.collections.ObservableList;
import javafx.geometry.Point3D;
import javafx.scene.paint.Color;
import javafx.scene.paint.PhongMaterial;
import javafx.scene.shape.Box;
import javafx.scene.shape.CullFace;
import javafx.scene.shape.Cylinder;
import javafx.scene.shape.Mesh;
import javafx.scene.shape.MeshView;
import javafx.scene.shape.TriangleMesh;
import javafx.scene.transform.Rotate;
import javafx.scene.transform.Translate;

public class DrawElement {
	
	public static Cylinder drawLine(Point3D origin, Point3D target) {
	    Point3D yAxis = new Point3D(0, 1, 0);
	    Point3D diff = target.subtract(origin);
	    double height = diff.magnitude();

	    Point3D mid = target.midpoint(origin);
	    Translate moveToMidpoint = new Translate(mid.getX(), mid.getY(), mid.getZ());

	    Point3D axisOfRotation = diff.crossProduct(yAxis);
	    double angle = Math.acos(diff.normalize().dotProduct(yAxis));
	    Rotate rotateAroundCenter = new Rotate(-Math.toDegrees(angle), axisOfRotation);
	    Cylinder line = new Cylinder(0.2, height);
	    final PhongMaterial grayMaterial = new PhongMaterial();
        grayMaterial.setDiffuseColor(Color.GRAY);
        line.setMaterial(grayMaterial);
	    
	    line.getTransforms().addAll(moveToMidpoint, rotateAroundCenter);
	    return line;
	}
	
	public static Box drawBox(Point3D origin, Point3D target, double w, double h){
		Point3D yAxis = new Point3D(0, 1, 0);
	    Point3D diff = target.subtract(origin);
	    double height = diff.magnitude();

	    Point3D mid = target.midpoint(origin);
	    Translate moveToMidpoint = new Translate(mid.getX(), mid.getY(), mid.getZ());

	    Point3D axisOfRotation = diff.crossProduct(yAxis);
	    double angle = Math.acos(diff.normalize().dotProduct(yAxis));
	    Rotate rotateAroundCenter = new Rotate(-Math.toDegrees(angle), axisOfRotation);
	    Box box = new Box(w, height,h);	    
        box.getTransforms().addAll(moveToMidpoint, rotateAroundCenter);
	    return box;
	}
	
	public static Xform drawOrthographicFrustum(double R,double zenith, double azimuth, double sub_w, double sub_h,PhongMaterial volMtl){
		
		Xform re = new Xform();
		
		if(zenith == 0)
			zenith = 0.0000001;
		
		double phi = -(azimuth - 90) / 180.0 * Math.PI;
		double theta = zenith/180.0*Math.PI;
		double x = -R*Math.sin(theta)*Math.cos(phi);
		double z = R*Math.sin(theta)*Math.sin(phi);
		double y = R*Math.cos(theta);
		
		//
		double norm_distance = sub_h*0.5*Math.tan(theta)/R;
		
		Box box = DrawElement.drawBox(new Point3D(x, y, z), new Point3D(-x*norm_distance, -y*norm_distance, -z*norm_distance), sub_w, sub_h);
		box.setMaterial(volMtl);		
		re.getChildren().add(box);

		double up_x = -x * y / (x * x + z * z);
	    double up_z = -y * z / (x * x + z * z);
	    double theta_rotation = Math.toDegrees(Math.atan(up_x/up_z));
	    re.getTransforms().add(new Rotate(theta_rotation, x, y, z, new Point3D(-x, -y, -z)));
		return re;
	}
	
	public static Xform drawPerspectiveFrustum(Point3D origin, Point3D target, double fovx, double fovy, PhongMaterial volMtl){		
		Xform re = new Xform();
		
		//
		target = target.add(target.subtract(origin));
		
		Point3D yAxis = new Point3D(0, 1, 0);
	    Point3D diff = target.subtract(origin);
	    double height = diff.magnitude();

	    Point3D mid = target.midpoint(origin);
	    Translate moveToMidpoint = new Translate(mid.getX(), mid.getY(), mid.getZ());

	    Point3D axisOfRotation = diff.crossProduct(yAxis);
	    if(diff.getX() == 0 && diff.getZ()==0)
	    	axisOfRotation = new Point3D(0, 0, 1);
	    double angle = Math.acos(diff.normalize().dotProduct(yAxis));
	    Rotate rotateAroundCenter = new Rotate(-Math.toDegrees(angle), axisOfRotation);
	    
	    double half_fovx = 0.5*fovx/180.0*Math.PI;
	    double half_fovy = 0.5*fovy/180.0*Math.PI;
	    double tanx = Math.tan(half_fovx);
	    double tany = Math.tan(half_fovy);
	    
	    TriangleMesh mesh = new TriangleMesh();
	    double points[] = {origin.getX()+tanx*height,origin.getY()+height,tany*height+origin.getZ(),
	    		origin.getX()-tanx*height,origin.getY()+height,tany*height+origin.getZ(),
	    		origin.getX()-tanx*height,origin.getY()+height,-tany*height+origin.getZ(),
	    		origin.getX()+tanx*height,origin.getY()+height,-tany*height+origin.getZ(),
	    				   origin.getX(), origin.getY(), origin.getZ()};
	    
	    mesh.getPoints().addAll(toFloatArray(points));
	    int faces[] = {0,0,1,0,4,0,
 			   1,0,2,0,4,0,
 			   2,0,3,0,4,0,
 			   3,0,0,0,4,0
 			   };
	    
		mesh.getFaces().addAll(faces);
		mesh.getTexCoords().addAll(0,0);
		MeshView meshViewx = new MeshView(mesh);
		meshViewx.setCullFace(CullFace.NONE);
		re.getChildren().add(meshViewx);
		meshViewx.setMaterial(volMtl);
		
		//camera up direction
		double up_x = -diff.getX()*diff.getY()/(diff.getX()*diff.getX()+diff.getZ()*diff.getZ());
		double up_z = -diff.getY()*diff.getZ()/(diff.getX()*diff.getX()+diff.getZ()*diff.getZ());
		double theta = Math.toDegrees(Math.atan(up_x/up_z));
		
		if(!(diff.getX() == 0 && diff.getZ()==0))
			re.getTransforms().add(new Rotate(theta, origin.getX(), origin.getY(), origin.getZ(), diff));

		re.getTransforms().add(new Rotate(-Math.toDegrees(angle), origin.getX(), origin.getY(), origin.getZ(), axisOfRotation));
		
		return re;
	}
	
	public static Xform drawXYGrid(double xExtend, double zExtend, int numofLine){
		Xform gridGroup = new Xform();
		double xstart = -xExtend*0.5;
		double zstart = -zExtend*0.5;
		double xInterval = xExtend/(numofLine*1.0),zInterval=zExtend/(numofLine*1.0);
		for(int i=0;i<numofLine+1;i++){
			//x direction
			gridGroup.getChildren().add(drawLine(new Point3D(xstart+i*xInterval, 0, zstart), 
					new Point3D(xstart+i*xInterval, 0, -zstart)));
			gridGroup.getChildren().add(drawLine(new Point3D(xstart, 0, zstart+zInterval*i), 
					new Point3D(-xstart, 0, zstart+zInterval*i)));
		}
		return gridGroup;
	}
	
	public static float[] toFloatArray(double[] arr) {
		  if (arr == null) return null;
		  int n = arr.length;
		  float[] ret = new float[n];
		  for (int i = 0; i < n; i++) {
		    ret[i] = (float)arr[i];
		  }
		  return ret;
		}
	
	public static Box drawPlane(double xExtend, double zExtend){
		Box plane = new Box(xExtend,0.05,zExtend);
		final PhongMaterial yellowMaterial = new PhongMaterial();
		yellowMaterial.setDiffuseColor(new Color(0.8862, 0.651, 0.2745, 1));
		yellowMaterial.setSpecularColor(new Color(0.8862, 0.651, 0.2745, 1));
		yellowMaterial.setSpecularPower(Double.POSITIVE_INFINITY);
		plane.setMaterial(yellowMaterial);
		return plane;
	}
	
	public static Xform drawObj(String filepath){
		
		ObjModelImporter objImporter = new ObjModelImporter();
		try {
		    objImporter.read(filepath);            
		}
		catch (ImportException e) {
		    // handle exception
		}
		MeshView[] meshViews = objImporter.getImport();
		objImporter.close();
		
		final PhongMaterial yellowMaterial = new PhongMaterial();
		yellowMaterial.setDiffuseColor(new Color(0.8862, 0.651, 0.2745, 1));
		yellowMaterial.setSpecularColor(new Color(0.8862, 0.651, 0.2745, 1));
		yellowMaterial.setSpecularPower(Double.POSITIVE_INFINITY);
		
		for(int i=0;i<meshViews.length;i++){
			meshViews[i].setMaterial(yellowMaterial);
			meshViews[i].setCullFace(CullFace.NONE);
		}
		Xform meshXform = new Xform();
		meshXform.getChildren().addAll(meshViews);
		meshXform.setRotateY(180);
		meshXform.setRotateZ(180);
		return meshXform;
	}
	
	/**
	 * 
	 * @param objPath
	 * @return
	 */
	public static Mesh[] getMeshFromObj(String objPath){
		ObjModelImporter objImporter = new ObjModelImporter();
		try {
		    objImporter.read(objPath);
		}
		catch (ImportException e) {
		    // handle exception
			e.printStackTrace();
		}
		MeshView[] meshViews = objImporter.getImport();
		objImporter.close();
		
		Mesh[] allmeshes = new Mesh[meshViews.length];
		
		for(int i=0;i<meshViews.length;i++){
			allmeshes[i] = meshViews[i].getMesh();
		}
		return allmeshes;
	}
	
	/**
	 * get all the mesh from a list of object
	 * @param objectsList
	 * @param parentPath
	 * @return
	 */
	public static ArrayList<Mesh> getMeshlistFromObjList(ObservableList<String> objectsList, String parentPath){
		ArrayList<Mesh> allMeshes = new ArrayList<Mesh>();
		for(int i=0;i<objectsList.size();i++){
			String objName = objectsList.get(i);
			String objPath = Paths.get(parentPath, objName).toString();
			Mesh[] objMeshes = getMeshFromObj(objPath);
			for(int j=0;j<objMeshes.length;j++){
				allMeshes.add(objMeshes[j]);
			}
		}
		return allMeshes;
	}
	
	/**
	 * convert mesh
	 * @param meshlist
	 */
	public static Xform ConvertMeshList2xform(ArrayList<Mesh> meshlist, ArrayList<Color> compColorList){
		Xform objXform = new Xform();
		for(int i=0;i<meshlist.size();i++){
			
			final PhongMaterial darkGreen = new PhongMaterial();
			darkGreen.setDiffuseColor(compColorList.get(i));
			darkGreen.setSpecularColor(compColorList.get(i));
			darkGreen.setSpecularPower(Double.POSITIVE_INFINITY);
			
			MeshView meshView = new MeshView(meshlist.get(i));
			meshView.setMaterial(darkGreen);
			meshView.setCullFace(CullFace.NONE);
			objXform.getChildren().add(meshView);
		}
//		objXform.setRotateY(180);
		objXform.setRotateX(180);
		return objXform;
	}
	/**
	 * 
	 * @param objectsList
	 * @param parentPath
	 * @return
	 */
	public static Xform drawObjectsList(ObservableList<String> objectsList, String parentPath){
		Xform objXform = new Xform();
		for(int i=0;i<objectsList.size();i++){
			String objName = objectsList.get(i);
			String objPath = Paths.get(parentPath, objName).toString();
			Xform objMeshXform = drawObj(objPath);
			objXform.getChildren().add(objMeshXform);
		}
		objXform.setRotateY(180);
		objXform.setRotateZ(180);
		
		return objXform;
	}
	
	
}
