import { Suspense } from 'react'

import DocumentsTable from '@/app/ui/dashboard/documents/documents-table'
import UploadPDFForm from '@/app/ui/dashboard/documents/upload-pdf-form'
import { lusitana } from '@/app/ui/fonts'

import { getDocumentsDocumentGet } from '@/app/lib/orval/src/document-management/document-management'
import { getAllDocumentTypesDocumentTypesGet } from '@/app/lib/orval/src/document-types/document-types'

export default async function DocumentsPage() {
    const documentsResponse = await getDocumentsDocumentGet()
    const documentTypesResponse = await getAllDocumentTypesDocumentTypesGet()

    return (
        <main>
            <h1 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>Documents</h1>
            <div className='mt-6 grid grid-cols-1 gap-6 md:grid-cols-3'>
                <div className='md:col-span-1'>
                    {documentTypesResponse.status === 200 ? (
                        <UploadPDFForm data={documentTypesResponse.data} />
                    ) : null}
                </div>
                <div className='md:col-span-2'>
                    <Suspense fallback={<div>Loading documents...</div>}>
                        {documentsResponse.status === 200 ? (
                            <DocumentsTable data={documentsResponse.data} />
                        ) : (
                            <div>Error loading documents.</div>
                        )}
                    </Suspense>
                </div>
            </div>
        </main>
    )
}
