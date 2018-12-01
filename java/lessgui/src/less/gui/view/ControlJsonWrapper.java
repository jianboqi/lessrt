package less.gui.view;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.nio.file.Paths;
import java.util.Iterator;

import org.json.JSONObject;
import org.json.JSONTokener;

import com.google.gson.JsonObject;
import com.sun.jmx.remote.internal.ServerNotifForwarder;

import javafx.scene.control.Alert;
import javafx.scene.control.Toggle;
import less.gui.helper.PyLauncher;
import less.gui.model.AtmosphereParams;
import less.gui.model.FacetOptical;
import less.gui.model.ProspectDParams;
import less.gui.model.SunPos;
import less.gui.utils.Const;

/**
 * Save all control data to json file, or load from json file
 * @author Jim
 *
 */
public class ControlJsonWrapper {
		
	//optical db
//	private TableView<String> opticalTable;
	private LessMainWindowController mwcontroller;
	
	public ControlJsonWrapper(LessMainWindowController lessmwController){
		this.mwcontroller = lessmwController;
	}
	
	public Boolean checkInput(){
		//check band num
		String bands = this.mwcontroller.sensorBandsField.getText();
		String skyl =  this.mwcontroller.atsPercentageField.getText();
		String[] bandsNum = bands.trim().split(",");
		String[] skyls = skyl.trim().split(",");
		if(bandsNum.length != skyls.length)
		{
			this.mwcontroller.outputConsole.logError("Number of bands is not the same as SKY percentage.\n");
			return false;
		}
			
		return true;
	}
	
	public String controltoJson(){
		JSONObject json=new JSONObject();		
	    JSONObject observation = new JSONObject();
	    // Different camera has different view geometry
	    String sensorType = this.mwcontroller.comboBoxSensorType.getSelectionModel().getSelectedItem();
	    if(sensorType.equals(Const.LESS_SENSOR_TYPE_ORTH) || sensorType.equals(Const.LESS_SENSOR_TYPE_PT) ){
	    	observation.put("obs_zenith", Double.parseDouble(this.mwcontroller.obsZenithField.getText().replaceAll(",", "")));
	    	observation.put("obs_azimuth", Double.parseDouble(this.mwcontroller.obsAzimuthField.getText().replaceAll(",", "")));
	    	observation.put("obs_R", Double.parseDouble(this.mwcontroller.obsAGLField.getText().replaceAll(",", "")));
	    }
	    
	    if(sensorType.equals(Const.LESS_SENSOR_TYPE_PER) || sensorType.equals(Const.LESS_SENSOR_TYPE_CF)){
	    	observation.put("obs_o_x", Double.parseDouble(this.mwcontroller.pers_o_x_field.getText().replaceAll(",", "")));
	    	observation.put("obs_o_y", Double.parseDouble(this.mwcontroller.pers_o_y_field.getText().replaceAll(",", "")));
	    	observation.put("obs_o_z", Double.parseDouble(this.mwcontroller.pers_o_z_field.getText().replaceAll(",", "")));
	    	observation.put("obs_t_x", Double.parseDouble(this.mwcontroller.pers_t_x_field.getText().replaceAll(",", "")));
	    	observation.put("obs_t_y", Double.parseDouble(this.mwcontroller.pers_t_y_field.getText().replaceAll(",", "")));
	    	observation.put("obs_t_z", Double.parseDouble(this.mwcontroller.pers_t_z_field.getText().replaceAll(",", "")));
	    	observation.put("relative_height", this.mwcontroller.CameraPosRelativeHeightCheckbox.isSelected());
	    }
	  
	    json.put("observation", observation);
	    
	    //illumination
	    JSONObject illumination = new JSONObject();
	    JSONObject sun = new JSONObject();
	    sun.put("sun_zenith", Double.parseDouble(this.mwcontroller.sunZenithField.getText().replaceAll(",", "")));
	    sun.put("sun_azimuth", Double.parseDouble(this.mwcontroller.sunAzimuthField.getText().replaceAll(",", "")));
	    illumination.put("sun", sun);
	    JSONObject atmosphere = new JSONObject();
	    // currently, only one choice
	    atmosphere.put("ats_type", this.mwcontroller.atsTypeCombobox.getSelectionModel().getSelectedItem());
	    if(this.mwcontroller.ThermalCheckbox.isSelected()) {
	    	atmosphere.put("AtsTemperature", this.mwcontroller.projManager.comboBoxSkyTemper.getSelectionModel().getSelectedItem());
	    }
	    if(this.mwcontroller.atsTypeCombobox.getSelectionModel().getSelectedItem().equals(Const.LESS_ATS_TYPE_SKY)) {
		    atmosphere.put("percentage", this.mwcontroller.atsPercentageField.getText());
	    }else {
	    	if(this.mwcontroller.projManager.atmosphereParams != null) {
	    		atmosphere.put("AtsParams", this.mwcontroller.projManager.atmosphereParams.toJsonObject());
	    	}    	
	    }
	    illumination.put("atmosphere", atmosphere);
	    json.put("illumination",illumination);
	    
	    if(this.mwcontroller.SolarSpectrumCheckbox.isSelected()){
	    	sun.put("sun_spectrum",this.mwcontroller.SolarSpectrumSunTextField.getText());
	    	atmosphere.put("sky_spectrum", this.mwcontroller.SolarSpectrumSkyTextField.getText());
	    }
	    //sun calculator
	    if(this.mwcontroller.projManager.sunpos != null){
	    	illumination.put("sun_calculator", true);
	    	illumination.put("calculator_params", this.mwcontroller.projManager.sunpos.toJsonObject());
	    }else{
	    	illumination.put("sun_calculator", false);
	    }
	    
	    
	    
	    //sensor
	    JSONObject sensor = new JSONObject();
	   // sensor.put("obs_R", 3000);
	    sensor.put("image_width", Integer.parseInt(this.mwcontroller.sensorWidthField.getText().replaceAll(",", "")));
	    sensor.put("image_height", Integer.parseInt(this.mwcontroller.sensorHeightField.getText().replaceAll(",", "")));
	    sensor.put("film_type", this.mwcontroller.ImageFormatRadioroup.getSelectedToggle().getUserData().toString());
	    sensor.put("bands", this.mwcontroller.sensorBandsField.getText());
	    if(this.mwcontroller.firstOrderCheckbox.isSelected()){
	    	sensor.put("record_only_direct", 2);
	    }else{
	    	//Due to the permutation of Halton QMC, the maximum number of interation is limited, we set it to 200
	    	//https://mitsuba.wiki.fc2.com/wiki/Halton%20QMC%20sampler%20%28halton%29
	    	sensor.put("record_only_direct", 200);
	    }
	    sensor.put("thermal_radiation", this.mwcontroller.ThermalCheckbox.isSelected());
	    sensor.put("NoDataValue", Double.parseDouble(this.mwcontroller.sensorNoDataValueField.getText()));
	    sensor.put("RepetitiveScene", Integer.parseInt(this.mwcontroller.sensorRepetitiveSceneTextField.getText()));
	    
	    sensor.put("sensor_type", sensorType);
	    
	    if(sensorType.equals(Const.LESS_SENSOR_TYPE_ORTH)) {
	    	sensor.put("hasFourComponentProduct", this.mwcontroller.orthfourCompsCheckbox.isSelected());
	    }
	    
	    if(sensorType.equals(Const.LESS_SENSOR_TYPE_ORTH) || sensorType.equals(Const.LESS_SENSOR_TYPE_PT)){
	    	JSONObject orthographic = new JSONObject();
		    orthographic.put("sample_per_square_meter", Integer.parseInt(this.mwcontroller.sensorSampleField.getText().replaceAll(",", "")));
		    orthographic.put("sub_region_width", Double.parseDouble(this.mwcontroller.sensorXExtentField.getText().replaceAll(",", "")));
		    orthographic.put("sub_region_height", Double.parseDouble(this.mwcontroller.sensorYExtentField.getText().replaceAll(",", "")));
		    orthographic.put("cover_whole_scene", this.mwcontroller.CoverWholeSceneCheckbox.isSelected());
		    sensor.put("orthographic", orthographic);
	    }
	    if(sensorType.equals(Const.LESS_SENSOR_TYPE_PER)){
	    	JSONObject perspective = new JSONObject();
	    	perspective.put("fovx", Double.parseDouble(this.mwcontroller.xfovField.getText()));
	    	perspective.put("fovy", Double.parseDouble(this.mwcontroller.yfovField.getText()));
	    	perspective.put("fovAxis", "diagonal");
	    	perspective.put("sample_per_square_meter", Integer.parseInt(this.mwcontroller.sensorSampleField.getText().replaceAll(",", "")));
	    	sensor.put("perspective", perspective);
	    	sensor.put("hasFourComponentProduct", this.mwcontroller.perfourCompsCheckbox.isSelected());
	    }
	    
	    if(sensorType.equals(Const.LESS_SENSOR_TYPE_CF)){
	    	JSONObject circularFisheye = new JSONObject();
	    	circularFisheye.put("angular_fov", Double.parseDouble(this.mwcontroller.cfFovTextField.getText()));
	    	circularFisheye.put("sample_per_square_meter", Integer.parseInt(this.mwcontroller.sensorSampleField.getText().replaceAll(",", "")));
	    	circularFisheye.put("projection_type", this.mwcontroller.combobox.getSelectionModel().getSelectedItem());
	    	sensor.put("CircularFisheye", circularFisheye);
	    }
	    
	    if(sensorType.equals(Const.LESS_SENSOR_TYPE_PT)){
	    	JSONObject photontracing = new JSONObject();
	    	photontracing.put("sunRayResolution", Double.parseDouble(mwcontroller.illumResTextField.getText().replaceAll(",", "")));
	    	photontracing.put("BRFProduct", mwcontroller.productBRFCheckbox.isSelected());
	    	if(mwcontroller.productBRFCheckbox.isSelected()) {
	    		photontracing.put("virtualDirections", mwcontroller.virtualDirTextField.getText());
	    		photontracing.put("NumberOfDirections",Integer.parseInt( mwcontroller.numOfDirectionTextField.getText()));
	    		photontracing.put("virtualDetectorDirections", mwcontroller.virtualDetectorTextField.getText());
	    	}
	    	photontracing.put("UpDownProduct", mwcontroller.productUpDownRadiationCheckbox.isSelected());
	    	photontracing.put("fPARProduct", mwcontroller.productfPARChecbox.isSelected());
	    	if(mwcontroller.productfPARChecbox.isSelected()) {
	    		if(mwcontroller.fPARLayerTextEdit.getText().equals("")) {
	    			Alert alert = new Alert(Alert.AlertType.ERROR);
				    alert.setTitle("Error...");
				    alert.setHeaderText("Error");
				    alert.setContentText("Layer definition can not be empty!");
				    alert.showAndWait();
	    		}
	    		photontracing.put("LayerDefinition", mwcontroller.fPARLayerTextEdit.getText());
	    	}
	    	
	    	sensor.put("PhotonTracing", photontracing);
	    }
	    
	    //virutal plane
	    if(this.mwcontroller.virtualPlaneCheckbox.isSelected()){
	    	JSONObject virtual_plane = new JSONObject();
	    	virtual_plane.put("vx", this.mwcontroller.projManager.xpos.getText());
	    	virtual_plane.put("vy", this.mwcontroller.projManager.ypos.getText());
	    	virtual_plane.put("vz", this.mwcontroller.projManager.zpos.getText());
	    	virtual_plane.put("sizex", this.mwcontroller.projManager.xsizepos.getText());
	    	virtual_plane.put("sizey", this.mwcontroller.projManager.ysizepos.getText());
	    	sensor.put("virtualPlane", virtual_plane);
	    }
	    json.put("sensor", sensor);
	    
	    	    
	    //scene optical
	    
	    JSONObject scene = new JSONObject();
	    JSONObject optical_properties = new JSONObject();
	    for(int i=0;i<this.mwcontroller.opticalData.size();i++){
	    	
	    	JSONObject oneOptical = new JSONObject();
	    	
	    	FacetOptical facetOptical = this.mwcontroller.opticalData.get(i);
	    	String opticalVal = facetOptical.getReflectanceFront()+";"+
							    	facetOptical.getReflectanceBack()+";"+
							    			facetOptical.getTransmittance();
	    	oneOptical.put("value", opticalVal);
	    	oneOptical.put("Type", facetOptical.getOpType());
	    	if(facetOptical.getOpType() == Const.LESS_OP_TYPE_PROSPECT_D) {
	    		oneOptical.put("ProspectDParams", this.mwcontroller.projManager.prospectDParamsMap.get(facetOptical.getOpticalName()).toJsonObject());
	    	}
	    	
	    	optical_properties.put(facetOptical.getOpticalName(), oneOptical);
	    }
	    scene.put("optical_properties", optical_properties);
	    JSONObject temperature_properties = new JSONObject();
	    for(int i=0;i<this.mwcontroller.projManager.temperatureList.size();i++){
	    	String tName = this.mwcontroller.projManager.temperatureList.get(i);
	    	String tVal = this.mwcontroller.temperatureMap.get(tName);
	    	temperature_properties.put(tName, tVal);
	    }
	    scene.put("temperature_properties", temperature_properties);
	    
	    JSONObject terrain = new JSONObject();
	    if(this.mwcontroller.comboBoxDEMType.getSelectionModel().getSelectedItem().equals(Const.LESS_TERRAIN_PLANE)){
	    	terrain.put("terr_file","");
	    }else{
	    	terrain.put("terr_file",this.mwcontroller.terrFileField.getText());
	    }
	    
	    String selectedBRDFMode = this.mwcontroller.terrainBRDFTypeCombox.getSelectionModel().getSelectedItem();
	    terrain.put("terrBRDFType", selectedBRDFMode);
	    if(selectedBRDFMode.equals(Const.LESS_TERRAIN_BRDF_LAMBERTIAN)) {
	    	String selectedOptical = this.mwcontroller.terrainOpticalCombox.getSelectionModel().getSelectedItem();
		    if (selectedOptical == null){
		    	terrain.put("optical", Const.LESS_DEFAULT_OPTICAL2);
		    }else{
		    	terrain.put("optical", selectedOptical);
		    }
	    }else if (selectedBRDFMode.equals(Const.LESS_TERRAIN_BRDF_SOILSPECT)) {
			JSONObject soilspect  = new JSONObject();
			soilspect.put("albedo", this.mwcontroller.albedoTextField.getText());
			soilspect.put("c1", this.mwcontroller.c1TextField.getText());
			soilspect.put("c2", this.mwcontroller.c2TextField.getText());
			soilspect.put("c3", this.mwcontroller.c3TextField.getText());
			soilspect.put("c4", this.mwcontroller.c4TextField.getText());
			soilspect.put("h1", this.mwcontroller.h1TextField.getText());
			soilspect.put("h2", this.mwcontroller.h2TextField.getText());
			terrain.put("soilSpectParams", soilspect);
		}else if(selectedBRDFMode.equals(Const.LESS_TERRAIN_BRDF_LANDALBEDOMAP)) {
			//land albedo
		    if(this.mwcontroller.landAlbedoTextField.getText().equals("")) {
		    	mwcontroller.outputConsole.log("Land Albedo Map is empty.\n");
		    }
		    terrain.put("landalbedo", this.mwcontroller.landAlbedoTextField.getText());
		}
	    
	    if(this.mwcontroller.ThermalCheckbox.isSelected()){
	    	terrain.put("temperature", this.mwcontroller.projManager.comboBoxTerrainTemper.getSelectionModel().getSelectedItem());
	    }
	    
	    //land cover
	    Boolean landcover = this.mwcontroller.landcoverCheckbox.isSelected();
	    if(landcover){
	    	this.mwcontroller.projManager.saveLandcover2File();
	    	terrain.put("landcover", Const.LESS_TERRAIN_LANDCOVER_FILE);
	    }
	    
	    terrain.put("optical_scale", 1);
	    terrain.put("extent_width", Double.parseDouble(this.mwcontroller.sceneXSizeField.getText().replaceAll(",", "")));
	    terrain.put("extent_height", Double.parseDouble(this.mwcontroller.sceneYSizeField.getText().replaceAll(",", "")));
	    terrain.put("terrain_type", this.mwcontroller.comboBoxDEMType.getSelectionModel().getSelectedItem());
	    scene.put("terrain", terrain);
	    JSONObject forest = new JSONObject();
	    forest.put("tree_pos_file", Const.LESS_INSTANCE_FILE_NAME);
	    forest.put("objects_file", Const.LESS_OBJECTS_FILE_NAME);
	    forest.put("CacheOBJFile", this.mwcontroller.objFileCacheChecbox.isSelected());
	    scene.put("forest", forest);
	    scene.put("extra_scene", "");
	    json.put("scene",scene);
	    
	    JSONObject Advanced = new JSONObject();
	   // Advanced.put("virtual_plane", this.mwcontroller.virtualPlaneCheckbox.isSelected());
	    Advanced.put("minimum_iteration", Integer.parseInt(this.mwcontroller.minIterTextField.getText()));
	    Advanced.put("network_sim", this.mwcontroller.projManager.isNetworkSim);
	    Advanced.put("number_of_cores", Integer.parseInt(this.mwcontroller.NumberofCoresTextField.getText()));
	    if(!this.mwcontroller.PyInterpreterEdit.getText().equals("")){
	    	Advanced.put("external_py_interpreter", this.mwcontroller.PyInterpreterEdit.getText());
	    }
	    json.put("Advanced", Advanced);
	    
	    
	    return json.toString(2);
	}
	
	
	public void json2controls(){
		String parameter_file_path = Paths.get(this.mwcontroller.simulation_path,
				this.mwcontroller.constConfig.data.getString("input_dir"),
				this.mwcontroller.constConfig.data.getString("config_file")).toString();
		if(!(new File(parameter_file_path).exists())){
			return;
		}
		JSONTokener jsonTokener = null;
		try {
			jsonTokener = new JSONTokener(new FileReader(new File(parameter_file_path)));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}  
		JSONObject data = new JSONObject(jsonTokener);
		
		
		//sensor
		JSONObject sensor = data.getJSONObject("sensor");
		
		if(sensor.getInt("record_only_direct") == -1 || sensor.getInt("record_only_direct") == 200){
			this.mwcontroller.firstOrderCheckbox.setSelected(false);
		}else{
			this.mwcontroller.firstOrderCheckbox.setSelected(true);
		}
		this.mwcontroller.ThermalCheckbox.setSelected(sensor.getBoolean("thermal_radiation"));
		if(sensor.has("NoDataValue")){
			this.mwcontroller.sensorNoDataValueField.setText(sensor.getDouble("NoDataValue")+"");
		}
		if(sensor.has("RepetitiveScene")) {
			this.mwcontroller.sensorRepetitiveSceneTextField.setText(sensor.getInt("RepetitiveScene")+"");
		}
		this.mwcontroller.sensorWidthField.setText(sensor.getInt("image_width")+"");
		this.mwcontroller.sensorHeightField.setText(sensor.getInt("image_height")+"");
		this.mwcontroller.sensorBandsField.setText(sensor.getString("bands"));
		this.mwcontroller.comboBoxSensorType.getSelectionModel().select(sensor.getString("sensor_type"));
		
		if(sensor.getString("sensor_type").equals(Const.LESS_SENSOR_TYPE_ORTH)){
			JSONObject camera = sensor.getJSONObject("orthographic");
			this.mwcontroller.CoverWholeSceneCheckbox.setSelected(camera.getBoolean("cover_whole_scene"));
			this.mwcontroller.projManager.handleWholeSceneCheckbox();
			this.mwcontroller.sensorXExtentField.setText(camera.getDouble("sub_region_width")+"");
			this.mwcontroller.sensorYExtentField.setText(camera.getDouble("sub_region_height")+"");
			this.mwcontroller.sensorSampleField.setText(camera.getInt("sample_per_square_meter")+"");
			this.mwcontroller.virtualPlaneCheckbox.setDisable(false);
			
			if(sensor.has("hasFourComponentProduct"))
				this.mwcontroller.orthfourCompsCheckbox.setSelected(sensor.getBoolean("hasFourComponentProduct"));
			else
				this.mwcontroller.orthfourCompsCheckbox.setSelected(false);
		}
		
		if(sensor.getString("sensor_type").equals(Const.LESS_SENSOR_TYPE_PER)){
			JSONObject camera = sensor.getJSONObject("perspective");
			this.mwcontroller.xfovField.setText(camera.getDouble("fovx")+"");
			this.mwcontroller.yfovField.setText(camera.getDouble("fovy")+"");
			this.mwcontroller.sensorSampleField.setText(camera.getInt("sample_per_square_meter")+"");
			this.mwcontroller.virtualPlaneCheckbox.setDisable(true);
			
			if(sensor.has("hasFourComponentProduct"))
				this.mwcontroller.perfourCompsCheckbox.setSelected(sensor.getBoolean("hasFourComponentProduct"));
			else
				this.mwcontroller.perfourCompsCheckbox.setSelected(false);
		}
		
		if(sensor.getString("sensor_type").equals(Const.LESS_SENSOR_TYPE_CF)){
			JSONObject camera = sensor.getJSONObject("CircularFisheye");
			this.mwcontroller.cfFovTextField.setText(camera.getDouble("angular_fov")+"");
			this.mwcontroller.sensorSampleField.setText(camera.getInt("sample_per_square_meter")+"");
			this.mwcontroller.combobox.getSelectionModel().select(camera.getString("projection_type"));
			this.mwcontroller.virtualPlaneCheckbox.setDisable(true);
		}
		
		if(sensor.getString("sensor_type").equals(Const.LESS_SENSOR_TYPE_PT)){
			JSONObject camera = sensor.getJSONObject("PhotonTracing");
			this.mwcontroller.illumResTextField.setText(camera.getDouble("sunRayResolution")+"");
			if(camera.has("BRFProduct")) {
				this.mwcontroller.productBRFCheckbox.setSelected(camera.getBoolean("BRFProduct"));
				if(camera.has("virtualDirections"))
					this.mwcontroller.virtualDirTextField.setText(camera.getString("virtualDirections"));
				if(camera.has("NumberOfDirections"))
					this.mwcontroller.numOfDirectionTextField.setText(camera.getInt("NumberOfDirections")+"");
				if(camera.has("virtualDetectorDirections"))
					this.mwcontroller.virtualDetectorTextField.setText(camera.getString("virtualDetectorDirections"));
			}
			if(camera.has("UpDownProduct")) this.mwcontroller.productUpDownRadiationCheckbox.setSelected(camera.getBoolean("UpDownProduct"));
			if(camera.has("fPARProduct")) {
				this.mwcontroller.productfPARChecbox.setSelected(camera.getBoolean("fPARProduct"));
				if(camera.has("LayerDefinition"))
					this.mwcontroller.fPARLayerTextEdit.setText(camera.getString("LayerDefinition"));
				}
			
			this.mwcontroller.virtualPlaneCheckbox.setDisable(false);
	    }
		
		String imageformat = sensor.getString("film_type");
		if(imageformat.equals(Const.LESS_OUT_IMAGEFORMAT_SPECTRUM)){
			this.mwcontroller.spectrumRadio.setSelected(true);
		}
		else{
			this.mwcontroller.rgbRadio.setSelected(true);
		}
		
	    if(sensor.has("virtualPlane")){
	    	this.mwcontroller.virtualPlaneCheckbox.setSelected(true);
	    	this.mwcontroller.projManager.handlePlaneCheckbox();
	    	JSONObject virtualPlaneObj = sensor.getJSONObject("virtualPlane");
	    	this.mwcontroller.projManager.xpos.setText(virtualPlaneObj.getString("vx"));
	    	this.mwcontroller.projManager.ypos.setText(virtualPlaneObj.getString("vy"));
	    	this.mwcontroller.projManager.zpos.setText(virtualPlaneObj.getString("vz"));
	    	this.mwcontroller.projManager.xsizepos.setText(virtualPlaneObj.getString("sizex"));
	    	this.mwcontroller.projManager.ysizepos.setText(virtualPlaneObj.getString("sizey"));
	    }else {
	    	this.mwcontroller.virtualPlaneCheckbox.setSelected(false);
	    }
				
	    JSONObject scene = data.getJSONObject("scene");		
	  //thermal
		if(this.mwcontroller.ThermalCheckbox.isSelected()){
			this.mwcontroller.projManager.handleThermalRadiationCheckbox();
			JSONObject temperature_properties = scene.getJSONObject("temperature_properties");
			Iterator<?> tkeys = temperature_properties.keys();
			this.mwcontroller.projManager.temperatureList.clear();
			this.mwcontroller.temperatureMap.clear();
			while( tkeys.hasNext() ) {
			    String key = (String)tkeys.next();
			    String value = temperature_properties.getString(key);
			    String [] vals = value.trim().split(";");
			    this.mwcontroller.projManager.temperatureList.add(key);
			    this.mwcontroller.temperatureMap.put(key, value);
			}
		}
			    
		//illumination
		JSONObject illumination = data.getJSONObject("illumination");
		JSONObject sun = illumination.getJSONObject("sun");
		this.mwcontroller.sunZenithField.setText(sun.getDouble("sun_zenith")+"");
		this.mwcontroller.sunAzimuthField.setText(sun.getDouble("sun_azimuth")+"");
		JSONObject ats = illumination.getJSONObject("atmosphere");
		String ats_type = ats.getString("ats_type");
		this.mwcontroller.atsTypeCombobox.getSelectionModel().select(ats_type);

		if(ats.has("AtsTemperature") && this.mwcontroller.ThermalCheckbox.isSelected()) {
			this.mwcontroller.projManager.comboBoxSkyTemper.getSelectionModel().select(ats.getString("AtsTemperature"));
		}
		if(ats_type.equals(Const.LESS_ATS_TYPE_SKY)) {
			this.mwcontroller.atsPercentageField.setText(ats.getString("percentage"));
		}else {
			if(ats.has("AtsParams")) {
				AtmosphereParams atmosphereParams = new AtmosphereParams();
				atmosphereParams.fromJsonObject(ats.getJSONObject("AtsParams"));
				this.mwcontroller.projManager.atmosphereParams = atmosphereParams;
			}		
		}
		
		//solar spectrum
		if(ats.has("sky_spectrum")){
			this.mwcontroller.SolarSpectrumCheckbox.setSelected(true);
			this.mwcontroller.SolarSpectrumSkyTextField.setText(ats.getString("sky_spectrum"));
		}
			
		if(sun.has("sun_spectrum")){
			this.mwcontroller.SolarSpectrumCheckbox.setSelected(true);
			this.mwcontroller.SolarSpectrumSunTextField.setText(sun.getString("sun_spectrum"));
		}
			
		//sun calculator
		
	    if(illumination.getBoolean("sun_calculator")){
	    	SunPos sunPos = new SunPos();
	    	sunPos.fromJsonObject(illumination.getJSONObject("calculator_params"));
	    	this.mwcontroller.projManager.sunpos = sunPos;
	    }
		
		//observation
		JSONObject observation = data.getJSONObject("observation");
		if(sensor.getString("sensor_type").equals(Const.LESS_SENSOR_TYPE_ORTH)){
			this.mwcontroller.obsZenithField.setText(observation.getDouble("obs_zenith")+"");
			this.mwcontroller.obsAzimuthField.setText(observation.getDouble("obs_azimuth")+"");
			this.mwcontroller.obsAGLField.setText(observation.getDouble("obs_R")+"");
		}
		
		if(sensor.getString("sensor_type").equals(Const.LESS_SENSOR_TYPE_PER) || sensor.getString("sensor_type").equals(Const.LESS_SENSOR_TYPE_CF)){
			this.mwcontroller.pers_o_x_field.setText(observation.getDouble("obs_o_x")+"");
			this.mwcontroller.pers_o_y_field.setText(observation.getDouble("obs_o_y")+"");
			this.mwcontroller.pers_o_z_field.setText(observation.getDouble("obs_o_z")+"");
			this.mwcontroller.pers_t_x_field.setText(observation.getDouble("obs_t_x")+"");
			this.mwcontroller.pers_t_y_field.setText(observation.getDouble("obs_t_y")+"");
			this.mwcontroller.pers_t_z_field.setText(observation.getDouble("obs_t_z")+"");
			if(observation.has("relative_height")){
				this.mwcontroller.CameraPosRelativeHeightCheckbox.setSelected(observation.getBoolean("relative_height"));
			}
			
		}
		
		//scene
		scene = data.getJSONObject("scene");
		//forest
		JSONObject forest = scene.getJSONObject("forest");
		if(forest.has("CacheOBJFile")) {
			this.mwcontroller.objFileCacheChecbox.setSelected(forest.getBoolean("CacheOBJFile"));
		}
		//optical reading
		JSONObject optical_properties = scene.getJSONObject("optical_properties");
		Iterator<?> keys = optical_properties.keys();
		this.mwcontroller.opticalData.clear();
		this.mwcontroller.terrainOpticalData.clear();
		// compatible to older versions
		while( keys.hasNext()) {
		    String key = (String)keys.next();
		    Object tmpObj = optical_properties.get(key);
		    if(tmpObj instanceof String) { //older projects
		    	 String value = optical_properties.getString(key);
				 String [] vals = value.trim().split(";");
				 this.mwcontroller.opticalData.add(new FacetOptical(key, vals[0],vals[1],vals[2], Const.LESS_OP_TYPE_MANUAL));
		    }
		    else {
		    	JSONObject opticalObj = optical_properties.getJSONObject(key);
		    	int opType = opticalObj.getInt("Type");
		    	if(opType == Const.LESS_OP_TYPE_PROSPECT_D) {
		    		String value = opticalObj.getString("value");
					String [] vals = value.trim().split(";");
					this.mwcontroller.opticalData.add(new FacetOptical(key, vals[0],vals[1],vals[2], Const.LESS_OP_TYPE_PROSPECT_D));
					ProspectDParams prospectDParams = new ProspectDParams();
					prospectDParams.fromJsonObject(opticalObj.getJSONObject("ProspectDParams"));
					this.mwcontroller.projManager.prospectDParamsMap.put(key, prospectDParams);
					
		    	}else if(opType == Const.LESS_OP_TYPE_DB) {
		    		String value = opticalObj.getString("value");
					String [] vals = value.trim().split(";");
					this.mwcontroller.opticalData.add(new FacetOptical(key, vals[0],vals[1],vals[2], Const.LESS_OP_TYPE_DB));
		    	}else if(opType == Const.LESS_OP_TYPE_MANUAL) {
		    		String value = opticalObj.getString("value");
					String [] vals = value.trim().split(";");
					this.mwcontroller.opticalData.add(new FacetOptical(key, vals[0],vals[1],vals[2], Const.LESS_OP_TYPE_MANUAL));
		    	}
		    }
		    
		    this.mwcontroller.terrainOpticalData.add(key);
		}
		
		
		//terrain
		JSONObject terrain = scene.getJSONObject("terrain");
		this.mwcontroller.sceneXSizeField.setText(terrain.getDouble("extent_width")+"");
		this.mwcontroller.sceneYSizeField.setText(terrain.getDouble("extent_height")+"");
		this.mwcontroller.comboBoxDEMType.getSelectionModel().select(terrain.getString("terrain_type"));
		if(terrain.getString("terrain_type").equals(Const.LESS_TERRAIN_MESH) ||
				terrain.getString("terrain_type").equals(Const.LESS_TERRAIN_RASTER)){
			this.mwcontroller.terrFileField.setText(terrain.getString("terr_file"));
		}
		
		if(terrain.has("terrBRDFType")) {
			String terrBRDFType = terrain.getString("terrBRDFType");
			this.mwcontroller.terrainBRDFTypeCombox.getSelectionModel().select(terrBRDFType);
			if(terrBRDFType.equals(Const.LESS_TERRAIN_BRDF_LAMBERTIAN)) {
				this.mwcontroller.terrainOpticalCombox.getSelectionModel().select(terrain.getString("optical"));
			}
			else if(terrBRDFType.equals(Const.LESS_TERRAIN_BRDF_SOILSPECT)){
				JSONObject soilspect = terrain.getJSONObject("soilSpectParams");
				this.mwcontroller.albedoTextField.setText(soilspect.getString("albedo"));
				this.mwcontroller.c1TextField.setText(soilspect.getString("c1"));
				this.mwcontroller.c2TextField.setText(soilspect.getString("c2"));
				this.mwcontroller.c3TextField.setText(soilspect.getString("c3"));
				this.mwcontroller.c4TextField.setText(soilspect.getString("c4"));
				this.mwcontroller.h1TextField.setText(soilspect.getString("h1"));
				this.mwcontroller.h2TextField.setText(soilspect.getString("h2"));
			}
			else if(terrBRDFType.equals(Const.LESS_TERRAIN_BRDF_LANDALBEDOMAP)) {
				if(terrain.has("landalbedo")) {
					this.mwcontroller.landAlbedoTextField.setText(terrain.getString("landalbedo"));
				}
			}
		}else {
			this.mwcontroller.terrainOpticalCombox.getSelectionModel().select(terrain.getString("optical"));
		}
		
		if(terrain.has("landcover")){
			this.mwcontroller.landcoverCheckbox.setSelected(true);
			this.mwcontroller.projManager.handleLandcoverCheckbox();//create listview control
			this.mwcontroller.projManager.readLandcover2File();
		}
		
		if(this.mwcontroller.ThermalCheckbox.isSelected()){
			this.mwcontroller.projManager.comboBoxTerrainTemper.getSelectionModel().select(terrain.getString("temperature"));
		}
		
		//advanced
		JSONObject advanced = data.getJSONObject("Advanced");	
	//	this.mwcontroller.virtualPlaneCheckbox.setSelected(advanced.getBoolean("virtual_plane"));
		this.mwcontroller.minIterTextField.setText(advanced.getInt("minimum_iteration")+"");
		this.mwcontroller.projManager.isNetworkSim = advanced.getBoolean("network_sim");
		
		int number_of_cores = advanced.getInt("number_of_cores");
		if(number_of_cores == -1){
			this.mwcontroller.NumberofCoresTextField.setText(Runtime.getRuntime().availableProcessors()+"");
		}else{
			this.mwcontroller.NumberofCoresTextField.setText(number_of_cores+"");
		}
		if(advanced.has("external_py_interpreter")){
			this.mwcontroller.PyInterpreterEdit.setText(advanced.getString("external_py_interpreter"));
			PyLauncher.external_py_interpreter = advanced.getString("external_py_interpreter");
		}
		
		
	}
	
	
	
}
