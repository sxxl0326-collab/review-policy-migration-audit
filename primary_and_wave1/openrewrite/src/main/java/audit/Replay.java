package audit;
import com.fasterxml.jackson.databind.*;
import org.openrewrite.*;
import org.openrewrite.internal.InMemoryLargeSourceSet;
import org.openrewrite.github.ReplaceDependabotReviewersWithCodeowners;
import org.openrewrite.yaml.YamlParser;
import org.openrewrite.yaml.tree.Yaml;
import org.openrewrite.text.PlainTextParser;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.io.*;
public final class Replay {
 public static void main(String[] args) throws Exception {
  ObjectMapper mapper=new ObjectMapper(); JsonNode cases=mapper.readTree(new File(args[0]));
  List<Map<String,Object>> records=new ArrayList<>();
  for(JsonNode item:cases){
   Map<String,Object> row=new LinkedHashMap<>();String id=item.get("id").asText();row.put("id",id);
   Path base=Paths.get(item.get("input").asText());Path out=Paths.get(item.get("output").asText());Files.createDirectories(out);
   List<String> errors=new ArrayList<>();InMemoryExecutionContext ctx=new InMemoryExecutionContext(t->{StringWriter sw=new StringWriter();t.printStackTrace(new PrintWriter(sw));errors.add(sw.toString());});
   List<SourceFile> sources=new ArrayList<>();Map<String,String> content=new LinkedHashMap<>();long start=System.nanoTime();
   try {
    for(String rel:List.of(".github/dependabot.yml",".github/dependabot.yaml",".github/CODEOWNERS","CODEOWNERS","docs/CODEOWNERS")){
     Path file=base.resolve(rel);if(!Files.isRegularFile(file))continue;String text=Files.readString(file,StandardCharsets.UTF_8);content.put(rel,text);
     java.util.stream.Stream<SourceFile> parsed=rel.endsWith(".yml")||rel.endsWith(".yaml")?YamlParser.builder().build().parse(ctx,text):PlainTextParser.builder().build().parse(ctx,text);
     parsed.forEach(sf->sources.add(sf.withSourcePath(Paths.get(rel))));
    }
    row.put("input_files",content.keySet());row.put("parsed_types",sources.stream().map(x->x.getClass().getName()).toList());
    boolean bad=sources.stream().anyMatch(x->x.getClass().getName().endsWith("ParseError"));
    if(bad)throw new IllegalStateException("Input parser produced ParseError");
    Recipe recipe=new ReplaceDependabotReviewersWithCodeowners(null);
    RecipeRun run=recipe.run(new InMemoryLargeSourceSet(sources),ctx);List<Result> results=run.getChangeset().getAllResults();
    List<String> diffs=new ArrayList<>();
    for(Result result:results){
     if(result.getBefore()!=null)content.remove(result.getBefore().getSourcePath().toString().replace('\\','/'));
     if(result.getAfter()!=null)content.put(result.getAfter().getSourcePath().toString().replace('\\','/'),result.getAfter().printAll());
     diffs.add(result.diff());
    }
    for(Map.Entry<String,String> entry:content.entrySet()){
     Path dest=out.resolve(entry.getKey());Files.createDirectories(dest.getParent());Files.writeString(dest,entry.getValue(),StandardCharsets.UTF_8);
    }
    Files.writeString(out.resolve("transformation.diff"),String.join("\n",diffs),StandardCharsets.UTF_8);
    row.put("status",errors.isEmpty()?"EXECUTED":"EXECUTED_WITH_REPORTED_ERRORS");row.put("changed_files",results.size());
   }catch(Throwable ex){row.put("status","FAILED");StringWriter sw=new StringWriter();ex.printStackTrace(new PrintWriter(sw));row.put("exception",sw.toString());}
   row.put("errors",errors);row.put("elapsed_seconds",(System.nanoTime()-start)/1e9);records.add(row);
   System.out.println(id+" "+row.get("status")+" "+row.get("elapsed_seconds"));
   mapper.writerWithDefaultPrettyPrinter().writeValue(new File(args[1]),records);
  }
 }
}
