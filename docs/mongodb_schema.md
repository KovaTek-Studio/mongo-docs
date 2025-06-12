# MongoDB Schema: `overdrivefx`

## 🗂 `payments`
- Estimated: 2 docs
- Sampled: 2 docs
### Fields:
- `_id`: ObjectId
- `studentId`: str
- `amount`: float
- `currency`: str
- `method`: str
- `status`: str
- `transactionId`: str
- `createdAt`: str

## 🗂 `collectiontest`
- Estimated: 0 docs
- Sampled: 0 docs
### Fields:

## 🗂 `roles`
- Estimated: 3 docs
- Sampled: 3 docs
### Fields:
- `_id`: ObjectId
- `name`: str
- `permissions`: list

## 🗂 `contacts`
- Estimated: 1 docs
- Sampled: 1 docs
### Fields:
- `_id`: ObjectId
- `telefono`: str
- `email`: str
- `instagram_url`: str
- `facebook_url`: str
- `whatsapp_url`: str
- `tiktok_url`: str
- `linkedin_url`: str
- `direccion`: str

## 🗂 `users`
- Estimated: 2 docs
- Sampled: 2 docs
### Fields:
- `_id`: ObjectId
- `email`: str
- `password`: str
- `roles`: list
- `permissions`: list
- `profile.name`: str
- `profile.phone`: str
- `profile.avatar`: str
- `profile.joinedAt`: str
- `status`: str
- `lastLogin`: str

## 🗂 `leads`
- Estimated: 2 docs
- Sampled: 2 docs
### Fields:
- `_id`: ObjectId
- `name`: str
- `email`: str
- `phone`: str
- `sourceCampaign`: str
- `createdAt`: str
- `convertedToStudent`: bool

## 🗂 `testimonials`
- Estimated: 7 docs
- Sampled: 7 docs
### Fields:
- `_id`: ObjectId
- `nombre`: str
- `email`: str
- `fecha`: datetime
- `texto`: str
- `rating`: int
- `aprobado`: bool
- `imagenes`: list

## 🗂 `analytics`
- Estimated: 2 docs
- Sampled: 2 docs
### Fields:
- `_id`: ObjectId
- `userId`: NoneType, str
- `event`: str
- `metadata.path`: str
- `metadata.referrer`: str
- `createdAt`: str
- `metadata.form`: str
- `metadata.fields`: int

## 🗂 `courses`
- Estimated: 2 docs
- Sampled: 2 docs
### Fields:
- `_id`: ObjectId
- `title`: str
- `description`: str
- `modules[0].moduleId`: str
- `modules[0].title`: str
- `modules[0].order`: int
- `price`: float
- `createdAt`: str
- `updatedAt`: str

## 🗂 `notifications`
- Estimated: 2 docs
- Sampled: 2 docs
### Fields:
- `_id`: ObjectId
- `userId`: str
- `type`: str
- `payload.subject`: str
- `payload.body`: str
- `status`: str
- `sentAt`: NoneType, str
- `retryCount`: int
- `payload.message`: str

