package less;

import javafx.animation.PauseTransition;
import javafx.application.Platform;
import javafx.application.Preloader;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.TextAlignment;
import javafx.stage.Stage;
import javafx.stage.StageStyle;
import javafx.util.Duration;
import less.gui.utils.Const;

public class LessMainPreloader extends Preloader {

    private static final double WIDTH = 400;
    private static final double HEIGHT = 300;

    private Stage preloaderStage;
    private Scene scene;

   // private Label progress;

    public LessMainPreloader() {
        // Constructor is called before everything.   
    	}

    @Override
    public void init() throws Exception {
        // If preloader has complex UI it's initialization can be done in MyPreloader#init
        Platform.runLater(() -> {
            BorderPane borderPane = new BorderPane();
            String image = LessMainPreloader.class.getResource("less_splash.png").toExternalForm();
            borderPane.setStyle("-fx-background-image: url('" + image + "'); " +
                       "-fx-background-repeat: stretch;");
            
//           borderPane.setStyle("-fx-background-color: green;");
            Label info = new Label("Loading, please wait...");
            info.setTextAlignment(TextAlignment.CENTER);
            info.setTextFill(Color.WHITE);
            //progress = new Label("0%");

            VBox root = new VBox(info);
            root.setAlignment(Pos.BOTTOM_CENTER);
            BorderPane.setAlignment(root, Pos.CENTER);
            borderPane.setCenter(root);
            
            Label version = new Label("  "+Const.LESS_VERSION);
            version.setTextFill(Color.WHITE);
            borderPane.setBottom(version);
            
            scene = new Scene(borderPane, WIDTH, HEIGHT);
        });
    }

    @Override
    public void start(Stage primaryStage) throws Exception {
        this.preloaderStage = primaryStage;
        preloaderStage.initStyle(StageStyle.UNDECORATED);
        // Set preloader scene and show stage.
        preloaderStage.setScene(scene);
        preloaderStage.setAlwaysOnTop(true);
        preloaderStage.show();
    }

    @Override
    public void handleApplicationNotification(PreloaderNotification info) {
        // Handle application notification in this point (see MyApplication#init).
//        if (info instanceof ProgressNotification) {
//            progress.setText(((ProgressNotification) info).getProgress() + "%");
//        }
    }

    @Override
    public void handleStateChangeNotification(StateChangeNotification info) {
        // Handle state change notifications.
        StateChangeNotification.Type type = info.getType();
        switch (type) {
            case BEFORE_LOAD:
                // Called after MyPreloader#start is called.
                break;
            case BEFORE_INIT:
                // Called before MyApplication#init is called.
                break;
            case BEFORE_START:
                // Called after MyApplication#init and before MyApplication#start is called.
            	PauseTransition delay = new PauseTransition(Duration.seconds(1.5));
            	delay.setOnFinished( event -> preloaderStage.close() );
            	delay.play();
               // preloaderStage.hide();
                break;
        }
    }
}
