/*
Copyright 2019 RazzMatazzBaz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

public class Install
{
	static readonly string ModuleName = "PivotTool";
	static readonly string ModuleVersion = "1.0.0.0";
	static readonly string[] ModuleData = new string[0];

	enum MayaInstall
	{
		M2013_x64,
		M2014_x64,
		M2015_x64,
		M2016,
		M2017,
		M2018,
		M2019
	}

	static readonly Dictionary<MayaInstall, string> VersionToPathName = new Dictionary<MayaInstall, string>()
	{
		{ MayaInstall.M2013_x64, "2013-x64" },
		{ MayaInstall.M2014_x64, "2014-x64" },
		{ MayaInstall.M2015_x64, "2015-x64" },
		{ MayaInstall.M2016, "2016" },
		{ MayaInstall.M2017, "2017" },
		{ MayaInstall.M2018, "2018" },
		{ MayaInstall.M2019, "2019" },
	};

	// JB: Add install sources here, add extra folders for each version
	static readonly Dictionary<MayaInstall, string> VersionToInstallPath = new Dictionary<MayaInstall, string>()
	{
		{ MayaInstall.M2018, "." },
		{ MayaInstall.M2019, "." },
	};

	/// <summary>
	/// 
	/// </summary>
	public static void Main()
	{
		// Get installation user directories filtered by whatever this script targets
		var installations = FindMayaInstallations().Where(kvp => VersionToInstallPath.ContainsKey(kvp.Key));

		foreach(var kvp in installations)
		{
			Console.WriteLine("Installing module for '{0}'...", kvp.Key);

			var installPath = Path.GetFullPath(Path.Combine(Environment.CurrentDirectory, VersionToInstallPath[kvp.Key]));
			var moduleDir = Path.Combine(kvp.Value, "modules");
			var modulePath = Path.Combine(moduleDir, ModuleName + ".mod");

			// There isn't a 'modules' dir by default, so make it
			TouchDir(moduleDir);

			// Build the module document
			var moduleBuilder = new StringBuilder();
			moduleBuilder.AppendLine(string.Format("+ {0} {1} {2}", ModuleName, ModuleVersion, installPath));

			foreach (var data in ModuleData)
			{
				moduleBuilder.AppendLine(data);
			}

			// Write it!
			Console.WriteLine("    Writing module...");
			File.WriteAllText(modulePath, moduleBuilder.ToString());
		}

		Console.WriteLine("Done!");
	}

	/// <summary>
	/// Get a collection of maya user directories
	/// </summary>
	/// <returns></returns>
	static Dictionary<MayaInstall, string> FindMayaInstallations()
	{
		// I think you can override this with the MAYA_APP_DIR env var, but I've not seen that used in the wild...
		// If necessary, just grab that first and override this path
		var documents = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "maya");

		var output = new Dictionary<MayaInstall, string>();
		foreach (var kvp in VersionToPathName)
		{
			var installPath = Path.Combine(documents, kvp.Value);
			if (Directory.Exists(installPath))
			{
				output.Add(kvp.Key, installPath);
			}
		}

		return output;
	}

	/// <summary>
	/// Create a directory if it doesn't exist
	/// </summary>
	/// <param name="inDirectory"></param>
	static void TouchDir(string inDirectory)
	{
		if (!Directory.Exists(inDirectory))
		{
			Console.WriteLine("    Creating Directory: {0}", inDirectory);

			Directory.CreateDirectory(inDirectory);
		}
	}
}
