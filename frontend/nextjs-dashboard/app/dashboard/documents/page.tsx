import { Suspense } from 'react'
import DocumentsTable from '@/app/ui/dashboard/documents/documents-table'
import UploadPDFForm from '@/app/ui/dashboard/documents/upload-pdf-form'
import { lusitana } from '@/app/ui/fonts'
import { fetchDocuments } from '@/app/lib/data'

export default async function DocumentsPage() {
    const documents = await fetchDocuments()
    console.log('Fetched documents:', documents)

    return (
        <main>
            <h1 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>Documents</h1>
            <div className='mt-6 grid grid-cols-1 gap-6 md:grid-cols-3'>
                <div className='md:col-span-1'>
                    <UploadPDFForm />
                </div>
                <div className='md:col-span-2'>
                    <Suspense fallback={<div>Loading documents...</div>}>
                        <DocumentsTable documents={documents.documents} />
                    </Suspense>
                </div>
            </div>
        </main>
    )
}
