package less.gui.helper;

import java.io.IOException;
import java.io.OutputStream;

import javafx.application.Platform;
import javafx.scene.control.TextArea;

public class OutputConsole extends OutputStream {
	 public TextArea console;

     public OutputConsole(TextArea console) {
         this.console = console;
     }

     public void appendText(String valueOf) {
         Platform.runLater(() -> console.appendText(valueOf));
     }
     
     public void log(String valueOf){
    	 
    	 Platform.runLater(() -> console.appendText(valueOf));
     }
     
     public void setText(String valueOf){
    	 
    	 Platform.runLater(() -> console.setText(valueOf));
     }
     
     public void scrollToBottom(double value){
    	 Platform.runLater(() -> console.setScrollTop(value));
     }

     public void write(int b) throws IOException {
         appendText(String.valueOf((char)b));
     }
     public void logError(String valueOf){
    	 Platform.runLater(() -> console.setStyle("-fx-text-fill: red;"));
    	 Platform.runLater(() -> console.appendText(valueOf));
     }
     
     public void repalce(int start, int end, String text){
    	 if(start>=0 && end >=0 && end>=start && !text.equals(""))
    		 Platform.runLater(() -> console.replaceText(start, end, text));
     }
     
     public void insert(int index,String text){
    	 Platform.runLater(() -> console.insertText(index, text));
     }
     
     public void setNormalMode(){
    	 Platform.runLater(() -> console.setStyle("-fx-text-fill: black;"));
     }
     public void setErrorMode(){
    	 Platform.runLater(() -> console.setStyle("-fx-text-fill: red;"));
     }
 }
