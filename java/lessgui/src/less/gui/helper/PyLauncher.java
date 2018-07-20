package less.gui.helper;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;

import org.apache.commons.lang3.SystemUtils;
import org.junit.experimental.theories.Theories;

import javafx.application.Platform;
import less.gui.utils.Const;
import less.gui.view.LessMainWindowController;

/**
 * run python scripts
 * @author Jim
 *
 */

public class PyLauncher extends Thread{
	
	private String sim_path;
	private Operation operation;
	private Thread t;
	private CountDownLatch latch;
	private OutputConsole bdConsole;
	public Process p=null; //current process
	private boolean isStop=false;
	private static final String WINDOWS_KILL = "taskkill /F /IM ";
	private static final String LINUX_KILL = "pkill ";
	
	public static String external_py_interpreter = "";
	
	private LessMainWindowController mwController;
	private boolean isRunningLess = false;
	
	private String userData;//for some tmp usage;
	private String userData2;
	private String userData3;
	private String userData4;
	
	
	public enum Operation {
	    NEW_SIM, GENERATE_V_I, GENERATE_3D_MODEL,
	    RUN_LESS,RUN_ALL,SAVE_AS,RUN_BATCH,RUN_BRF,RUN_BT,
	    RUN_TREE_DETECTION, GENERATE_TERRAIN, GENERATE_TREEHEIGHT_FOR_3DVIWER
	}
	
	public static String getPyexe(){
		if(!external_py_interpreter.equals("")){
			return external_py_interpreter;
		}
		String pypath;
		if(Const.LESS_MODE.equals("development")){
//			if(SystemUtils.IS_OS_LINUX){
//				pypath= Paths.get("/home/jimb/miniconda2/bin/","python").toString();
//			}else{
			pypath= Paths.get(Paths.get(System.getProperty("user.dir")).getParent().getParent().toString(),"Utility","Python36","python").toString();
//			}
			
		}else{
			if(SystemUtils.IS_OS_LINUX){
				pypath = Paths.get(System.getProperty("user.dir"), "bin/python/bin","python").toString();
			}else{
				 pypath = Paths.get(System.getProperty("user.dir"), "bin/python/","python").toString();
			}	   
		}
		return pypath;
	}
	
	public String getLessRTexe(){
		String pypath;
		if(Const.LESS_MODE.equals("development")){
			pypath= Paths.get(PyLauncher.getLessPyFolderPath(),"bin","rt",
					this.mwController.constConfig.data.getString("current_rt_program"),"lessrt").toString();
		}else{
			pypath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",
					"bin","rt",this.mwController.constConfig.data.getString("current_rt_program"),"lessrt").toString();
		}
		return pypath;
	}
	
	public static String getLessPyFolderPath(){
		return Paths.get(Paths.get(System.getProperty("user.dir")).getParent().getParent().toString(),"python","lesspy").toString();
	}
	
	
	public static String getScriptsPath(String scriptsName){
		String pypath;
		if(Const.LESS_MODE.equals("development")){
			pypath= Paths.get(PyLauncher.getLessPyFolderPath(), scriptsName+".py").toString();
		}else{
			pypath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",scriptsName+".py").toString();
		}
		return pypath;
	}
	
	public static String getUtilityScriptsPath(String scriptsName){
		String pypath;
		if(Const.LESS_MODE.equals("development")){
			pypath = Paths.get(PyLauncher.getLessPyFolderPath(), "Utility", scriptsName+".py").toString();
		}else{
			pypath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy","Utility",scriptsName+".py").toString();
		}
		return pypath;
	}
	
	public static String getDefaultConf(){
		String pypath;
		if(Const.LESS_MODE.equals("development")){
			pypath= Paths.get(PyLauncher.getLessPyFolderPath(), Const.LESS_DEFAULT_INPUT_FILE).toString();
		}else{
			pypath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",Const.LESS_DEFAULT_INPUT_FILE).toString();
		}
		return pypath;
	}
	
	public String getScriptsRoot(){
		
		String pypath;
		if(Const.LESS_MODE.equals("development")){
			pypath= Paths.get(PyLauncher.getLessPyFolderPath(), Const.LESS_LAUNCH_SCRIPT).toString();
		}else{
			pypath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",Const.LESS_LAUNCH_SCRIPT).toString();
		}
		return pypath;
	}
	
	public void prepare(String sim_path, Operation op,CountDownLatch latch, OutputConsole bdConsole){
		this.sim_path = sim_path;
		this.operation  = op;
		this.latch = latch;
		this.bdConsole = bdConsole;
		this.bdConsole.setNormalMode();
	}
	
	public void setTmpData(String data){
		this.userData = data;
	}
	
	public void setTmpData2(String data){
		this.userData2 = data;
	}
	
	public void setTmpData3(String data){
		this.userData3 = data;
	}
	
	public void setTmpData4(String data){
		this.userData4 = data;
	}
	
	public void setLessMainController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void run(){
		synchronized (this) {
			switch (this.operation) {
			case NEW_SIM:
				newsim();
				break;
			case GENERATE_V_I:
				generateViewIllumination();
				break;
			case GENERATE_3D_MODEL:
				generate_3d_model();
				break;
			case RUN_LESS:
				run_less();
				break;
			case RUN_ALL:
				run_all();
				break;
			case SAVE_AS:
				save_as();
				break;
			case RUN_BATCH:
				run_batch();
				break;
			case RUN_BRF:
				run_brf();
				break;
			case RUN_BT:
				run_bt();
				break;
			case RUN_TREE_DETECTION:
				run_tree_detection();
				break;
			case GENERATE_TERRAIN:
				generate_terrain_model();
				break;
			case GENERATE_TREEHEIGHT_FOR_3DVIWER:
				generate_3D_pos_of_objects();
				break;
			default:
				break;
			}
			this.latch.countDown();
			notify();
		}
		
	}
	
	public static void killLessRT(){
		try {
			if(SystemUtils.IS_OS_WINDOWS){
				Runtime.getRuntime().exec(WINDOWS_KILL + Const.LESS_RT_NAME_WINDOWS);
			}else{
				Runtime.getRuntime().exec(LINUX_KILL + Const.LESS_RT_NAME_LINUX);
			}
			
		} catch (IOException e) {
		}
	}
	
	public void stop_current_job(){
		try {
			if(SystemUtils.IS_OS_WINDOWS){
				Runtime.getRuntime().exec(WINDOWS_KILL + Const.LESS_RT_NAME_WINDOWS);
			}else{
				Runtime.getRuntime().exec(LINUX_KILL + Const.LESS_RT_NAME_LINUX);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		if(p != null){
			isStop = true;
			p.destroy();
			synchronized (this) {
				 notify();
			}
		}
		
	}
	
	public void stop_sim(){
		
		
	}
	
	public void stop_process(Process p){
		p.destroy();
		this.isRunningLess = false;
		synchronized (this) {
			 notify();
		}
	}
	
	public void start () {
	      if (t == null) {
	         t = new Thread (this, "pylauncher");
	         t.setUncaughtExceptionHandler((thread, throwable) -> {
	        	 bdConsole.setErrorMode();
	 			 bdConsole.log(throwable.getMessage());
	 			//When there exists some erros, go ahead to notify
	 			synchronized (this) {
	 				 notify();
	 			}
	 			
	         });
	         t.start ();
	      }
	   }
	
	/**
	 * Control the output of less
	 * @param line
	 */
	private void controlOutputofLess(String line) throws Exception,IllegalArgumentException{
		
		if(Const.LESS_OUT_ALL){
			bdConsole.log(line+"\n");
			return;
		}
		
//		bdConsole.log(line+"\n");
		if (line.startsWith("INFO:")){
			bdConsole.log(line+"\n");
		}
		else if(line.contains("Starting simulation job")){
			bdConsole.log("INFO: "+line.substring(line.indexOf("Starting simulation job"), line.length())+"\n");
		}
		else if(line.startsWith("Simulating")){
			String text = this.bdConsole.console.getText();
			String [] arr = text.split("\n");
			String lastText = arr[arr.length-1];
			if(lastText.startsWith("Simulating")){
				String substr = text.substring(0, text.length()-1);
				int start = substr.lastIndexOf("\n");
				bdConsole.repalce(start+1, bdConsole.console.getCaretPosition(), line+"\n");
			}else{
				bdConsole.log(line+"\n");
			}
		}
		else if(line.contains("Time:"))
		{
			bdConsole.log("INFO: "+line.substring(line.indexOf("Time:"), line.length())+"\n");
		}
		else if(line.contains("Writing image to")){
			bdConsole.log("INFO: "+line.substring(line.indexOf("Writing image to"), line.length()-8)+"\".\n");
		}
		else if(line.contains("Connecting to")){
			bdConsole.log("INFO: "+line.substring(line.indexOf("Connecting to"), line.length())+"\n");
		}
		else if(line.contains("Loading shape")){
			bdConsole.log("INFO: "+line.substring(line.indexOf("Loading shape"), line.length())+"\n");
		}
			
	}
	
	
	private void runProcess(ProcessBuilder pd){
		if(this.sim_path==null){
			return;
		}
		pd.directory(new File(sim_path));
		try {
//			pd.redirectErrorStream(true);
			p = pd.start();
			BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line;
			while ((line = input.readLine()) != null) {
				if(this.isRunningLess){
					try{
						controlOutputofLess(line);
					}catch (Exception e) {
					}
					continue;
				}else{
					bdConsole.appendText(line+"\n");
				}
				
			}
			input = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			while ((line = input.readLine()) != null) {
				bdConsole.setErrorMode();
				bdConsole.log(line+"\n");
			}
			p.waitFor();
		} catch (IOException | InterruptedException e) {
			e.printStackTrace();
		}
	}
	
	
	/**
	 * new project
	 */
	public void newsim(){
		//build the process
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsRoot(),"-n");
		runProcess(pd);
	}
	
	/**
	 * save project as 
	 */
	public void save_as(){
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsRoot(),"-s","\""+userData+"\"");
		runProcess(pd);
	}
	
	/**
	 * generate view and Illumination 
	 */
	public void generateViewIllumination(){
		//build the process
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsRoot(),"-g","v");
		runProcess(pd);
	}
	
	
	/**
	 * generate 3D
	 */
	public void generate_3d_model(){
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsRoot(),"-g","s");
		runProcess(pd);
	}
	
	/**
	 * generate terrain
	 */
	public void generate_terrain_model(){
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsRoot(),"-g","t");
		runProcess(pd);
	}
	
	/**
	 * 生成三维显示时所有的树木的高程程序，通过光线跟踪
	 */
	public void generate_3D_pos_of_objects(){
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsRoot(),"-g","m");
		runProcess(pd);
	}
	
	/**
	 * 
	 * 
	 */
	public void run_less(){
//		testRun();
		this.isRunningLess = true;
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsRoot(),"-r","n","-p", this.userData);
		runProcess(pd);
		this.isRunningLess = false;
	}
	
	/**
	 * run batch
	 */
	public void run_batch(){
		this.isRunningLess = true;
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsPath(Const.LESS_BATCH_SCRIPT_NAME),"--batchPath",this.userData);
		runProcess(pd);
		this.isRunningLess = false;
	}
	
	
	/**
	 * 计算BRF
	 */
	public void run_brf(){
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsPath(Const.LESS_SCRIPT_POST_PROCESSING),"-t","BRF");
		runProcess(pd);
	}
	
	/**
	 * run brightness temperature
	 */
	public void run_bt() {
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsPath(Const.LESS_SCRIPT_POST_PROCESSING),"-t","BT");
		runProcess(pd);
	}
	
	
	/**
	 * single tree detection
	 */
	public void run_tree_detection(){
		ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(),getScriptsPath(Const.LESS_SCRIPT_TREE_DETECTION),
				"-i", this.userData,"-l", this.userData2,"-c",this.userData3,"-b",this.userData4);
//		List<String> cmdstrs = pd.command();
//		for(int i=0;i<cmdstrs.size();i++){
//			bdConsole.appendText(cmdstrs.get(i)+" ");
//		}
		
		runProcess(pd);
		this.mwController.StopDrawTree = true;
		Platform.runLater(() -> this.mwController.projManager.treePosFromCHM_PostProcessing());
		this.mwController.StopDrawTree = false;
		Platform.runLater(() -> this.mwController.reDrawAll());
	}
	
	/**
	 * test
	 */
//	public void run_less(){
//		
//		String main_scene_file_path = Paths.get(this.sim_path,
//				this.mwController.constConfig.data.getString("input_dir"),
//				this.mwController.constConfig.data.getString("tmp_scene_file_dir"),
//				this.mwController.constConfig.data.getString("main_scene_xml_file")).toString();
//		String dist_name = this.mwController.constConfig.data.getString("spectral_img_prefix") + "_VZ=" + this.mwController.obsZenithField.getText() +
//                "_VA=" + this.mwController.obsAzimuthField.getText();
//		String dist_file_opath = Paths.get(this.sim_path,
//				this.mwController.constConfig.data.getString("output_dir"),
//				dist_name).toString();
//		bdConsole.log(main_scene_file_path+"\n");
//		bdConsole.log(dist_file_opath+"\n");
//		ProcessBuilder pd = new ProcessBuilder(this.getLessRTexe(),main_scene_file_path, "-o",dist_file_opath);
//		runProcess(pd);
//	}
	
	/**
	 * test
	 */
	public void testRun(){
		ProcessBuilder pd=new ProcessBuilder("E:\\Coding\\Mitsuba\\LessPy\\bin\\rt\\dist-30\\lessrt.exe",
			"E:\\Coding\\Repos\\JavaWorkspace\\LessGUI\\build\\deploy\\LESS-1.0beta\\ExampleSim\\Parameters\\_scenefile\\main.xml",
			"-o E:\\Coding\\Repos\\JavaWorkspace\\LessGUI\\build\\deploy\\LESS-1.0beta\\ExampleSim\\Results\\spectral__VZ=0_VA=180");
		runProcess(pd);
	}
	
	/**
	 * run all process
	 */
	public void run_all(){
		bdConsole.log("-----------------------------------------\n");
		if(!isStop)
			generate_3d_model();
		if(!isStop)
			generateViewIllumination();
		if(!isStop)
			run_less();
	}
	
	/**
	 * run static scripts
	 */
	public static ArrayList<String> runUtilityscripts(ProcessBuilder pd, OutputConsole bdConsole, String outName){
		ArrayList<String> reArrayList = new ArrayList<String>();
		try {
//			pd.redirectErrorStream(true);
			Process p = pd.start();
			BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line;
			while ((line = input.readLine()) != null) {
				String[] arr = line.trim().split(":");
				if(arr.length > 1 && arr[0].equals(outName))
					reArrayList.add(arr[1]);
				else
					bdConsole.appendText(line+"\n");
			}
			input = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			while ((line = input.readLine()) != null) {
				bdConsole.setErrorMode();
				bdConsole.log(line+"\n");
			}
			p.waitFor();
		} catch (IOException | InterruptedException e) {
			e.printStackTrace();
		}
		return reArrayList;
	}
	
}
