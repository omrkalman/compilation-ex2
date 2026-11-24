import java.io.*;
import java.nio.file.*;
import java.util.*;

/* Runs Main.main(in, out) for every "in<TAB>out" line of a list file inside one JVM.
 * Usage: java -cp PARSER:<dir of BatchRun.class> BatchRun list.tsv */
public class BatchRun
{
	public static void main(String[] args) throws Exception
	{
		PrintStream realOut = System.out;
		PrintStream nul = new PrintStream(OutputStream.nullOutputStream());
		List<String> lines = Files.readAllLines(Paths.get(args[0]));
		long t0 = System.nanoTime();
		int crashes = 0;
		for (String line : lines)
		{
			String[] p = line.split("\t");
			System.setOut(nul);
			System.setErr(nul);
			try { Main.main(new String[]{p[0], p[1]}); }
			catch (Throwable t) { crashes++; }
		}
		System.setOut(realOut);
		realOut.printf("ran %d inputs in %.1fs, %d uncaught crashes%n",
			lines.size(), (System.nanoTime() - t0) / 1e9, crashes);
	}
}
