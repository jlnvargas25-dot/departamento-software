import { createClient } from "@supabase/supabase-js";

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_KEY!);

export async function createTodo(text: string) {
  try {
    const { data, error } = await supabase.from("todos").insert({ text });
    if (error) throw error;
    return data;
  } catch (err) {
    // empty catch — should have structured logging
  }
}

export async function deleteTodo(id: string) {
  try {
    await supabase.from("todos").delete().eq("id", id);
  } catch (err) {
    // @intentional-silent
  }
}
