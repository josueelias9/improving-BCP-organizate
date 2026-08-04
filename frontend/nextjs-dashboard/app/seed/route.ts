import bcrypt from 'bcrypt'
import postgres from 'postgres'
import { users } from '@/app/lib/placeholder-data'

const sql = postgres(process.env.POSTGRES_URL!, { ssl: 'require' })

async function seedUsers() {
    // TODO: not sure if this is necessary, since the backend creates the user table. validate
    await sql`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`
    await sql`
    CREATE TABLE IF NOT EXISTS users (
      id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      email TEXT NOT NULL UNIQUE,
      password TEXT NOT NULL
    );
  `

    const insertedUsers = await Promise.all(
        users.map(async user => {
            const hashedPassword = await bcrypt.hash(user.password, 10)
            return sql`
        INSERT INTO users (id, name, email, password)
        VALUES (${user.id}, ${user.name}, ${user.email}, ${hashedPassword})
        ON CONFLICT (id) DO NOTHING;
      `
        })
    )

    return insertedUsers
}

export async function GET() {
    try {
        const result = await sql.begin(sql => [seedUsers()])

        return Response.json({ message: 'Database seeded successfully' })
    } catch (error) {
        return Response.json({ error }, { status: 500 })
    }
}
