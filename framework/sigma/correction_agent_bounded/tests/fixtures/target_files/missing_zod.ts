"use server";

export async function createItem(formData: FormData) {
  const title = formData.get("title") as string;
  const quantity = Number(formData.get("quantity"));
  const price = Number(formData.get("price"));

  // No zod validation on inputs
  await db.items.create({ title, quantity, price });
}
