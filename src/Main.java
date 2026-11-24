import java.io.*;
import java.io.PrintWriter;
import java_cup.runtime.Symbol;
import ast.*;

public class Main
{
	static public void main(String argv[])
	{
		Lexer l;
		Parser p;
		Symbol s;
		AstNode ast;
		FileReader fileReader;
		PrintWriter fileWriter = null;
		String inputFileName = argv[0];
		String outputFileName = argv[1];
		
		try
		{
			/********************************/
			/* [1] Initialize a file reader */
			/********************************/
			fileReader = new FileReader(inputFileName);

			/********************************/
			/* [2] Initialize a file writer */
			/********************************/
			fileWriter = new PrintWriter(outputFileName);
			
			/******************************/
			/* [3] Initialize a new lexer */
			/******************************/
			l = new Lexer(fileReader);
			
			/*******************************/
			/* [4] Initialize a new parser */
			/*******************************/
			p = new Parser(l);

			/***********************************/
			/* [5] 3 ... 2 ... 1 ... Parse !!! */
			/***********************************/
			ast = (AstNode) p.parse().value;

			/*****************************************************/
			/* [6] Parsing succeeded: write the result right away */
			/*****************************************************/
			fileWriter.print("OK");
			fileWriter.close();
			fileWriter = null;

			/**********************************************************/
			/* [7] Debug-only AST dump (needs ./output/ in the cwd).  */
			/*     Must never change the result written above.        */
			/**********************************************************/
			try
			{
				if (ast != null) ast.printMe();
				AstGraphviz.getInstance().finalizeFile();
			}
			catch (Throwable t)
			{
				/* ignore: debug output only */
			}
    	}
			     
		catch (Throwable e)
		{
			if (fileWriter != null)
			{
				fileWriter.print(e.getMessage() != null && e.getMessage().startsWith("ERROR") ? e.getMessage() : "ERROR");
				fileWriter.close();
			}
		}
	}
}