package less.gui.view;

import javafx.fxml.FXML;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;

public class HelpViewerController {
	@FXML
	private WebView HelpWebView;
	
	public void initView(String url){
		WebEngine webEngine = HelpWebView.getEngine();
//		System.out.println(getClass().getResource("/less.html").toString());
		webEngine.load(url);
	}
}
