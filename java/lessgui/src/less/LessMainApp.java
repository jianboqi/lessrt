package less;
	
import java.io.IOException;
import java.util.ArrayList;

import com.sun.javafx.application.LauncherImpl;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.scene.layout.BorderPane;
import javafx.stage.Stage;
import less.gui.view.LessMainWindowController;


public class LessMainApp extends Application {
	private Stage primaryStage;
	private BorderPane rootLayout;
	private Scene scene;
	public LessMainWindowController lessMainController;
	 private static final int COUNT_LIMIT = 500000;
	
	
	public void initRootLayout()
	{
		try
		{
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(LessMainApp.class.getResource("gui/view/LessMainWindowView.fxml"));
			rootLayout = (BorderPane) loader.load();
			scene = new Scene(rootLayout);
			lessMainController = loader.getController();
			lessMainController.setMainApp(this);
		}catch (IOException e){
			e.printStackTrace();
		}
	}
	
	/**
	 * python console
	 * 
	 */
	 @Override
    public void stop() throws Exception {
        Platform.exit();
        System.exit(0);
    }
	
	/**
     * Returns the main stage.
     * @return
     */
    public Stage getPrimaryStage() {
        return primaryStage;
    }
    
    @SuppressWarnings("restriction")
	@Override
    public void init() throws Exception {
    	initRootLayout();

    	// Perform some heavy lifting (i.e. database start, check for application updates, etc. )
//        for (int i = 0; i < COUNT_LIMIT; i++) {
//            double progress = (100 * i) / COUNT_LIMIT;
//            LauncherImpl.notifyPreloader(this, new Preloader.ProgressNotification(progress));
//        }
    }
    
    public ArrayList<Image> getIconList(){
    	ArrayList<Image> iconList = new ArrayList<Image>();
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS48_48.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS64_64.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS128_128.png")));
    	return iconList;
    }
    
    public ArrayList<Image> getIconListRed(){
    	ArrayList<Image> iconList = new ArrayList<Image>();
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16_red.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32_red.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS48_48_red.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS64_64_red.png")));
    	iconList.add(new Image(LessMainApp.class.getResourceAsStream("LESS128_128_red.png")));
    	return iconList;
    }
    
    
	@Override
	public void start(Stage primaryStage) {

		this.primaryStage = primaryStage;
		this.primaryStage.getIcons().addAll(getIconList());
		this.primaryStage.setTitle("LESS");
		this.primaryStage.setScene(scene);
		this.primaryStage.show();
		lessMainController.initView();
	}
	
	
	@SuppressWarnings("restriction")
	public static void main(String[] args) {
		//launch(args);
		LauncherImpl.launchApplication(LessMainApp.class, LessMainPreloader.class, args);
	}
}
