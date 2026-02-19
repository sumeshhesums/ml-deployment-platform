FROM node:20-alpine

WORKDIR /app

# Copy package files first
COPY package.json ./

# Install with legacy peer deps and skip optional
RUN npm install --legacy-peer-deps --no-optional

# Copy source files
COPY . .

# Build the app
RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
