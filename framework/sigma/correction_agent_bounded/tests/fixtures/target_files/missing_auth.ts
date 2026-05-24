"use server";

import { createClient } from "@/lib/supabase/server";

export async function updateProfile(formData: FormData) {
  const supabase = await createClient();
  const name = formData.get("name") as string;

  // Missing auth check — should verify user before updating
  const { error } = await supabase
    .from("profiles")
    .update({ name })
    .eq("id", formData.get("id"));

  if (error) throw error;
}
